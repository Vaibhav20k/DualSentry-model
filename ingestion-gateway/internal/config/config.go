package config

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	ServerPort string

	DBHost     string
	DBPort     string
	DBUser     string
	DBPassword string
	DBName     string
	KafkaBrokers []string
	KafkaTopic   string
}

func Load() (*Config, error) {

	// Load .env file (ignore if not found)
	_ = godotenv.Load()

	cfg := &Config{
		ServerPort: os.Getenv("SERVER_PORT"),

		DBHost:     os.Getenv("DB_HOST"),
		DBPort:     os.Getenv("DB_PORT"),
		DBUser:     os.Getenv("DB_USER"),
		DBPassword: os.Getenv("DB_PASSWORD"),
		DBName:     os.Getenv("DB_NAME"),
		KafkaBrokers: []string{os.Getenv("KAFKA_BROKERS")},
		KafkaTopic:   os.Getenv("KAFKA_TOPIC"),
	}

	if cfg.ServerPort == "" {
		cfg.ServerPort = "50051"
	}

	if cfg.DBHost == "" {
		return nil, fmt.Errorf("DB_HOST is required")
	}

	if cfg.DBPort == "" {
		return nil, fmt.Errorf("DB_PORT is required")
	}

	if cfg.DBUser == "" {
		return nil, fmt.Errorf("DB_USER is required")
	}

	if cfg.DBPassword == "" {
		return nil, fmt.Errorf("DB_PASSWORD is required")
	}

	if cfg.DBName == "" {
		return nil, fmt.Errorf("DB_NAME is required")
	}

	return cfg, nil
}