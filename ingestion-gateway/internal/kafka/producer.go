package kafka

import (
	"encoding/json"
	"log"
	"time"

	"github.com/IBM/sarama"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/metrics"
)

type Producer struct {
	producer sarama.SyncProducer
	topic    string
}

func NewProducer(
	brokers []string,
	topic string,
) (*Producer, error) {

	config := sarama.NewConfig()

	config.Version = sarama.V3_5_0_0
	config.Producer.Partitioner = sarama.NewHashPartitioner

	config.Producer.RequiredAcks = sarama.WaitForAll
	config.Producer.Return.Successes = true

	p, err := sarama.NewSyncProducer(brokers, config)
	if err != nil {
		return nil, err
	}

	log.Println("Kafka producer connected.")

	return &Producer{
		producer: p,
		topic:    topic,
	}, nil
}

func (p *Producer) Close() error {
	return p.producer.Close()
}

func (p *Producer) Publish(
	key string,
	value []byte,
) error {

	start := time.Now()

	msg := &sarama.ProducerMessage{
		Topic: p.topic,
		Key:   sarama.StringEncoder(key),
		Value: sarama.ByteEncoder(value),
	}

	partition, offset, err := p.producer.SendMessage(msg)

	metrics.KafkaPublishDuration.Observe(
		time.Since(start).Seconds(),
	)

	if err != nil {
		return err
	}

	metrics.KafkaMessagesPublished.Inc()

	log.Printf(
		"Published to Topic=%s Partition=%d Offset=%d",
		p.topic,
		partition,
		offset,
	)

	return nil
}

func (p *Producer) PublishJSON(
	key string,
	payload interface{},
) error {

	data, err := json.Marshal(payload)
	if err != nil {
		return err
	}

	return p.Publish(key, data)
}
