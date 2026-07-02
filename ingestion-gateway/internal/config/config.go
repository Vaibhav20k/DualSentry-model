package config

import (
	"fmt"
	"os"
)

type Config struct {
	ServerPort string
}

func Load() (*Config, error) {

	port := os.Getenv("SERVER_PORT")

	if port == "" {
		port = "50051"
	}

	cfg := &Config{
		ServerPort: port,
	}

	if cfg.ServerPort == "" {
		return nil, fmt.Errorf("server port cannot be empty")
	}

	return cfg, nil
}
