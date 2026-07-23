package server

import (
	"fmt"
	"net/http"
	"os"
	"time"
	"context"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/metrics"
	apihandler "github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/api/handler"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/config"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/postgres"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/kafka"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/service"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/ml"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/middleware"
)

type HTTPServer struct {
	server *http.Server
	port   string
}

func NewHTTPServer(
	cfg *config.Config,
) *HTTPServer {

	mux := http.NewServeMux()

	// PostgreSQL connection
	db, err := postgres.NewConnection(cfg)
	if err != nil {
		panic(err)
	}
	// Transaction repository
	transactionRepo := postgres.NewTransactionRepository(db)

	// Anomaly repository
	anomalyRepo := postgres.NewAnomalyRepository(db)

	// Baseline repositories
	baselineRepo := postgres.NewBaselineRepository(db)
	historyRepo := postgres.NewHistoryRepository(db)

	// Baseline updater
	baselineUpdater := service.NewBaselineUpdater(
		historyRepo,
		baselineRepo,
	)

	// Kafka producer
	producer, err := kafka.NewProducer(
		cfg.KafkaBrokers,
		cfg.KafkaTopic,
	)
	if err != nil {
		panic(err)
	}
	

	// ML Client
	mlClient := ml.NewClient("")

	// Prediction repository
	predictionRepo := postgres.NewFraudPredictionRepository(db)

	// Transaction service
	transactionService := service.NewTransactionService(
		transactionRepo,
		anomalyRepo,
		predictionRepo,
		baselineRepo,
		historyRepo,
		producer,
		baselineUpdater,
		mlClient,
	)

	// REST transaction handler
	transactionHandler := apihandler.NewTransactionHandler(
		transactionService,
	)

	// Prediction handler
	predictionHandler := apihandler.NewPredictionHandler(
		predictionRepo,
	)

	// Dashboard handler
	dashboardHandler := apihandler.NewDashboardHandler(
		predictionRepo,
	)

	mux.HandleFunc(
		"/health",
		apihandler.LiveHandler,
	)

	mux.HandleFunc(
		"/health/live",
		apihandler.LiveHandler,
	)

	mux.HandleFunc(
		"/health/ready",
		apihandler.ReadyHandler,
	)
	
	mux.Handle(
		"/metrics",
		promhttp.Handler(),
	)

	mux.HandleFunc(
		"/api/predictions",
		predictionHandler.GetAllPredictions,
	)

	mux.HandleFunc(
		"/api/dashboard/summary",
		dashboardHandler.GetSummary,
	)

	mux.HandleFunc(
    	"/api/dashboard/trend",
    	dashboardHandler.GetTrend,
	)
	mux.HandleFunc(
		"/api/transactions",
		transactionHandler.SubmitTransaction,
	)


	// Wrap mux with Prometheus metrics and CORS middleware
	handler := corsMiddleware(
		metricsMiddleware(
			middleware.RateLimit(mux),
		),
	)

	return &HTTPServer{
		server: &http.Server{
			Addr:    ":" + cfg.HTTPPort,
			Handler: handler,
		},
		port: cfg.HTTPPort,
	}
}

func (h *HTTPServer) Start() error {

	fmt.Printf(
		"🚀 REST API listening on port %s\n",
		h.port,
	)

	return h.server.ListenAndServe()
}

func (h *HTTPServer) Stop(ctx context.Context) error {
	return h.server.Shutdown(ctx)
}

type statusRecorder struct {
	http.ResponseWriter
	status int
}

func (r *statusRecorder) WriteHeader(code int) {
	r.status = code
	r.ResponseWriter.WriteHeader(code)
}

func metricsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

		start := time.Now()

		rec := &statusRecorder{
			ResponseWriter: w,
			status:         http.StatusOK,
		}

		next.ServeHTTP(rec, r)

		metrics.HTTPRequestsTotal.
			WithLabelValues(
				r.Method,
				r.URL.Path,
				fmt.Sprintf("%d", rec.status),
			).
			Inc()

		metrics.HTTPRequestDuration.
			WithLabelValues(
				r.Method,
				r.URL.Path,
			).
			Observe(time.Since(start).Seconds())
	})
}

// corsMiddleware handles CORS headers.
// The allowed origin is configurable via the CORS_ALLOWED_ORIGIN
// environment variable, defaulting to the local Vite dev server.
func corsMiddleware(next http.Handler) http.Handler {
	allowedOrigin := os.Getenv("CORS_ALLOWED_ORIGIN")
	if allowedOrigin == "" {
		allowedOrigin = "http://localhost:5173"
	}
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", allowedOrigin)
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}