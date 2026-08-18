package ratelimit

import (
	"context"
	"fmt"
	"time"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/cache"
)

const (
	DefaultLimit  = 100
	DefaultWindow = time.Minute
)

func Allow(
	ctx context.Context,
	key string,
	limit int,
	window time.Duration,
) (bool, error) {

	client := cache.GetRedisClient()

	counterKey := fmt.Sprintf("rate:%s", key)

	count, err := client.Incr(ctx, counterKey).Result()
	if err != nil {
		return false, err
	}

	if count == 1 {
		client.Expire(ctx, counterKey, window)
	}

	return count <= int64(limit), nil
}
