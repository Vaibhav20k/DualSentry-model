package config

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	ServerPort string
	HTTPPort   string

	DBHost     string
	DBPort     string
	DBUser     string
	DBPassword string
	DBName     string

	RedisHost string
	RedisPort string

	KafkaBrokers []string
	KafkaTopic   string

	MLServiceURL string
}

func Load() (*Config, error) {

	// Load .env file (ignore if not found)
	_ = godotenv.Load()

	cfg := &Config{
		ServerPort: getEnvWithDefault("SERVER_PORT", "50051"),
		HTTPPort:   getEnvWithDefault("HTTP_PORT", "8080"),

		DBHost:     os.Getenv("DB_HOST"),
		DBPort:     os.Getenv("DB_PORT"),
		DBUser:     os.Getenv("DB_USER"),
		DBPassword: os.Getenv("DB_PASSWORD"),
		DBName:     os.Getenv("DB_NAME"),

		RedisHost: getEnvWithDefault("REDIS_HOST", "localhost"),
		RedisPort: getEnvWithDefault("REDIS_PORT", "6379"),

		KafkaBrokers: []string{getEnvWithDefault("KAFKA_BROKERS", "localhost:9092")},
		KafkaTopic:   getEnvWithDefault("KAFKA_TOPIC", "transactions.raw"),

		MLServiceURL: getEnvWithDefault("ML_SERVICE_URL", "http://localhost:8000"),
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

func getEnvWithDefault(key, defaultValue string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return defaultValue
}