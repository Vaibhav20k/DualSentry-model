package ml

import (
	"time"

	"github.com/sony/gobreaker"
)

var PredictionBreaker = gobreaker.NewCircuitBreaker(
	gobreaker.Settings{
		Name: "ml-prediction",

		MaxRequests: 5,

		Interval: 60 * time.Second,

		Timeout: 30 * time.Second,

		ReadyToTrip: func(counts gobreaker.Counts) bool {
			return counts.ConsecutiveFailures >= 5
		},
	},
)
