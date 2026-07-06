package kafka

import (
	"encoding/json"
	"log"

	"github.com/IBM/sarama"
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

	msg := &sarama.ProducerMessage{
		Topic: p.topic,
		Key:   sarama.StringEncoder(key),
		Value: sarama.ByteEncoder(value),
	}

	_, _, err := p.producer.SendMessage(msg)

	return err
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