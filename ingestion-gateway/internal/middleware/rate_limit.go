package middleware

import (
	"net/http"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/metrics"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/ratelimit"
)

func RateLimit(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

		// Skip rate limiting for infrastructure endpoints
		switch r.URL.Path {
		case "/metrics", "/health", "/health/live", "/health/ready":
			next.ServeHTTP(w, r)
			return
		}

		ip := ClientIP(r)

		allowed, err := ratelimit.Allow(
			r.Context(),
			ip,
			ratelimit.DefaultLimit,
			ratelimit.DefaultWindow,
		)
		if err != nil {
			http.Error(
				w,
				"Rate limiter unavailable",
				http.StatusInternalServerError,
			)
			return
		}

		if !allowed {

			metrics.RateLimitRejected.
				WithLabelValues(r.URL.Path).
				Inc()

			http.Error(
				w,
				"Too Many Requests",
				http.StatusTooManyRequests,
			)
			return
		}

		next.ServeHTTP(w, r)
	})
}
