package kafka

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/IBM/sarama"

	retryerrors "github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/errors"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/decision"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/events"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/metrics"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/ml"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
)

const (
	maxRetryCount = 3
)

type Consumer struct {
	consumer sarama.Consumer
	topic    string

	baselineRepo repository.BaselineRepository
	historyRepo  repository.HistoryRepository

	predictionRepo repository.FraudPredictionRepository

	mlClient *ml.Client
	engine   *decision.Engine

	alertRepo *repository.AlertRepository

	retryProducer *Producer
	dlqProducer   *Producer
}

func NewConsumer(
	brokers []string,
	topic string,

	baselineRepo repository.BaselineRepository,
	historyRepo repository.HistoryRepository,
	predictionRepo repository.FraudPredictionRepository,

	mlClient *ml.Client,
	engine *decision.Engine,
	alertRepo *repository.AlertRepository,

	retryProducer *Producer,
	dlqProducer *Producer,
) (*Consumer, error) {

	c, err := sarama.NewConsumer(
		brokers,
		nil,
	)
	if err != nil {
		return nil, err
	}

	log.Println("Kafka consumer connected.")

	return &Consumer{
		consumer: c,
		topic:    topic,

		baselineRepo: baselineRepo,
		historyRepo:  historyRepo,

		predictionRepo: predictionRepo,

		mlClient: mlClient,
		engine:   engine,

		alertRepo: alertRepo,

		retryProducer: retryProducer,
		dlqProducer:   dlqProducer,
	}, nil
}
func (c *Consumer) consumeTopic(topic string) error {

	partitions, err := c.consumer.Partitions(topic)
	if err != nil {
		return err
	}

	log.Printf(
		"Listening on topic %s (%d partitions)...",
		topic,
		len(partitions),
	)

	for _, partition := range partitions {

		partitionConsumer, err := c.consumer.ConsumePartition(
			topic,
			partition,
			sarama.OffsetNewest,
		)
		if err != nil {
			return err
		}

		go func(
			pc sarama.PartitionConsumer,
			partition int32,
			topic string,
		) {
			defer pc.Close()

			log.Printf(
				"Listening on topic=%s partition=%d",
				topic,
				partition,
			)

			for message := range pc.Messages() {

				start := time.Now()

				var event events.TransactionEvent

				if err := json.Unmarshal(
					message.Value,
					&event,
				); err != nil {

					log.Printf(
						"Failed to decode event: %v",
						err,
					)
					continue
				}

				if err := c.processEvent(
					partition,
					event,
				); err != nil {

					log.Printf(
						"Processing failed: %v",
						err,
					)

					// Permanent errors are NOT retried.
					if !retryerrors.IsRetryable(err) {

						log.Printf(
							"Non-retryable error for transaction %s",
							event.TransactionID,
						)
						continue
					}

					if event.RetryCount < maxRetryCount {

						if err := c.publishToRetry(
							event,
						); err != nil {

							log.Printf(
								"Retry publish failed: %v",
								err,
							)
						}

					} else {

						if err := c.publishToDLQ(
							event,
						); err != nil {

							log.Printf(
								"DLQ publish failed: %v",
								err,
							)
						}
					}
				}

				metrics.KafkaConsumeDuration.Observe(
					time.Since(start).Seconds(),
				)

				metrics.KafkaMessagesConsumed.Inc()
			}

		}(partitionConsumer, partition, topic)
	}

	return nil
}

func (c *Consumer) Consume() error {

	if err := c.consumeTopic(
		c.topic,
	); err != nil {
		return err
	}

	select {}
}

func (c *Consumer) ConsumeRetry() error {

	if err := c.consumeTopic(
		"transactions.retry",
	); err != nil {
		return err
	}

	select {}
}
func (c *Consumer) processEvent(
	partition int32,
	event events.TransactionEvent,
) error {

	decision := c.engine.Decide(
		event.FraudProbability,
	)

	log.Printf(
		"[Partition %d] Transaction=%s Probability=%.4f Decision=%s",
		partition,
		event.TransactionID,
		event.FraudProbability,
		decision,
	)

	switch decision {

	case "ALLOW":

		metrics.DecisionCounter.
			WithLabelValues("ALLOW").
			Inc()

		log.Printf(
			"✅ Transaction %s allowed",
			event.TransactionID,
		)

		return nil

	case "REVIEW":

		metrics.DecisionCounter.
			WithLabelValues("REVIEW").
			Inc()

		if err := c.alertRepo.CreateManualReview(
			event.TransactionID,
			event.FraudProbability,
		); err != nil {

			// Infrastructure error → retry
			return retryerrors.NewRetryable(err)
		}

		log.Printf(
			"🟡 Manual review created for %s",
			event.TransactionID,
		)

		return nil

	case "BLOCK":

		metrics.DecisionCounter.
			WithLabelValues("BLOCK").
			Inc()

		if err := c.alertRepo.CreateFraudAlert(
			event.TransactionID,
			event.FraudProbability,
			"HIGH_RISK",
		); err != nil {

			// Infrastructure error → retry
			return retryerrors.NewRetryable(err)
		}

		log.Printf(
			"🔴 Fraud alert created for %s",
			event.TransactionID,
		)

		return nil

	default:

		// Business error → don't retry
		return fmt.Errorf(
			"unknown decision: %s",
			decision,
		)
	}
}

func (c *Consumer) publishToRetry(
	event events.TransactionEvent,
) error {

	event.RetryCount++
	metrics.RetryCounter.Inc()

	log.Printf(
		"Retrying transaction %s (attempt %d)",
		event.TransactionID,
		event.RetryCount,
	)

	return c.retryProducer.PublishJSON(
		event.TransactionID,
		event,
	)
}

func (c *Consumer) publishToDLQ(
	event events.TransactionEvent,
) error {

	metrics.DLQCounter.Inc()
	log.Printf(
		"Sending transaction %s to DLQ",
		event.TransactionID,
	)

	return c.dlqProducer.PublishJSON(
		event.TransactionID,
		event,
	)
}

func (c *Consumer) Close() error {

	var firstErr error

	if c.retryProducer != nil {
		if err := c.retryProducer.Close(); err != nil && firstErr == nil {
			firstErr = err
		}
	}

	if c.dlqProducer != nil {
		if err := c.dlqProducer.Close(); err != nil && firstErr == nil {
			firstErr = err
		}
	}

	if c.consumer != nil {
		if err := c.consumer.Close(); err != nil && firstErr == nil {
			firstErr = err
		}
	}

	return firstErr
}
