package cache

import (
	"context"
	"time"
)

const DashboardCacheTTL = 30 * time.Second

func GetDashboardSummary(
	ctx context.Context,
	destination any,
) (bool, error) {

	return Get(
		ctx,
		"dashboard:summary",
		destination,
	)
}

func SetDashboardSummary(
	ctx context.Context,
	value any,
) error {

	return Set(
		ctx,
		"dashboard:summary",
		value,
		DashboardCacheTTL,
	)
}

func GetDashboardTrend(
	ctx context.Context,
	destination any,
) (bool, error) {

	return Get(
		ctx,
		"dashboard:trend",
		destination,
	)
}

func SetDashboardTrend(
	ctx context.Context,
	value any,
) error {

	return Set(
		ctx,
		"dashboard:trend",
		value,
		DashboardCacheTTL,
	)
}
