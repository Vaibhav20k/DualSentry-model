package metrics

import "github.com/prometheus/client_golang/prometheus"

var (
	RateLimitRejected = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "gateway_rate_limit_rejected_total",
			Help: "Total number of requests rejected by the rate limiter.",
		},
		[]string{"path"},
	)

	HTTPRequestsTotal = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Total HTTP requests.",
		},
		[]string{"method", "path", "status"},
	)

	HTTPRequestDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_request_duration_seconds",
			Help:    "HTTP request latency.",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "path"},
	)

	MLPredictionDuration = prometheus.NewHistogram(
		prometheus.HistogramOpts{
			Name:    "ml_prediction_duration_seconds",
			Help:    "ML inference latency.",
			Buckets: prometheus.DefBuckets,
		},
	)

	KafkaPublishDuration = prometheus.NewHistogram(
		prometheus.HistogramOpts{
			Name:    "kafka_publish_duration_seconds",
			Help:    "Kafka publish latency.",
			Buckets: prometheus.DefBuckets,
		},
	)

	KafkaConsumeDuration = prometheus.NewHistogram(
		prometheus.HistogramOpts{
			Name:    "kafka_consume_duration_seconds",
			Help:    "Kafka consume latency.",
			Buckets: prometheus.DefBuckets,
		},
	)

	KafkaMessagesPublished = prometheus.NewCounter(
		prometheus.CounterOpts{
			Name: "kafka_messages_published_total",
			Help: "Kafka messages published.",
		},
	)

	KafkaMessagesConsumed = prometheus.NewCounter(
		prometheus.CounterOpts{
			Name: "kafka_messages_consumed_total",
			Help: "Kafka messages consumed.",
		},
	)

	DecisionCounter = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "fraud_decision_total",
			Help: "Fraud decision counts.",
		},
		[]string{"decision"},
	)

	RetryCounter = prometheus.NewCounter(
		prometheus.CounterOpts{
			Name: "retry_total",
			Help: "Retry attempts.",
		},
	)

	DLQCounter = prometheus.NewCounter(
		prometheus.CounterOpts{
			Name: "dlq_total",
			Help: "Dead-letter queue events.",
		},
	)
)

func Init() {

	prometheus.MustRegister(

		RateLimitRejected,

		HTTPRequestsTotal,
		HTTPRequestDuration,

		MLPredictionDuration,

		KafkaPublishDuration,
		KafkaConsumeDuration,

		KafkaMessagesPublished,
		KafkaMessagesConsumed,

		DecisionCounter,

		RetryCounter,
		DLQCounter,
	)
}
