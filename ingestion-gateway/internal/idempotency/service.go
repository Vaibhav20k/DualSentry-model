package idempotency

import (
	"context"
	"time"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/cache"
)

const (
	DefaultExpiration = 24 * time.Hour
)

func Exists(
	ctx context.Context,
	key string,
	destination any,
) (bool, error) {

	return cache.Get(
		ctx,
		key,
		destination,
	)
}

func Save(
	ctx context.Context,
	key string,
	response any,
) error {

	return cache.Set(
		ctx,
		key,
		response,
		DefaultExpiration,
	)
}

func Delete(
	ctx context.Context,
	key string,
) error {

	return cache.Delete(
		ctx,
		key,
	)
}
