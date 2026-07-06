package kafka

import (
	"log"

	"github.com/IBM/sarama"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
)

type Consumer struct {
	consumer sarama.Consumer
	topic    string
	baselineRepo repository.BaselineRepository
	historyRepo repository.HistoryRepository
}

func NewConsumer(
	brokers []string,
	topic string,
	baselineRepo repository.BaselineRepository,
	historyRepo repository.HistoryRepository,
) (*Consumer, error) {

	c, err := sarama.NewConsumer(brokers, nil)
	if err != nil {
		return nil, err
	}

	log.Println("Kafka consumer connected.")

	return &Consumer{
		consumer: c,
		topic:    topic,
		baselineRepo: baselineRepo,
		historyRepo: historyRepo,
	}, nil
}

func (c *Consumer) Consume() error {

	partitionConsumer, err := c.consumer.ConsumePartition(
		c.topic,
		0,
		sarama.OffsetNewest,
	)
	if err != nil {
		return err
	}

	defer partitionConsumer.Close()

	log.Printf("Listening on topic %s...\n", c.topic)

	for message := range partitionConsumer.Messages() {

		log.Printf(
			"Received: %s\n",
			string(message.Value),
		)
	}

	return nil
}

func (c *Consumer) Close() error {
	return c.consumer.Close()
}