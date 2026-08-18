package cache

import (
	"context"
	"encoding/json"
	"time"
)

func Set(
	ctx context.Context,
	key string,
	value any,
	expiration time.Duration,
) error {

	bytes, err := json.Marshal(value)
	if err != nil {
		return err
	}

	return GetRedisClient().
		Set(
			ctx,
			key,
			bytes,
			expiration,
		).Err()
}

func Get(
	ctx context.Context,
	key string,
	destination any,
) (bool, error) {

	result, err := GetRedisClient().
		Get(
			ctx,
			key,
		).Result()

	if err != nil {

		if err.Error() == "redis: nil" {
			return false, nil
		}

		return false, err
	}

	if err := json.Unmarshal(
		[]byte(result),
		destination,
	); err != nil {
		return false, err
	}

	return true, nil
}

func Delete(
	ctx context.Context,
	key string,
) error {

	return GetRedisClient().
		Del(
			ctx,
			key,
		).Err()
}
