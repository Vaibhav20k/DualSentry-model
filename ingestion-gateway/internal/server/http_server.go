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

// corsMiddleware handles CORS headers for cross-origin requests.
//
// When the frontend is served through the Nginx reverse proxy, all requests
// are same-origin (http://localhost → http://localhost), so no CORS is needed.
//
// When the frontend runs outside Docker (e.g., `npm run dev` on port 5173),
// the browser's Origin header is reflected back to allow the dev workflow.
//
// Behavior is configurable via the CORS_ALLOWED_ORIGIN environment variable:
//   - "reflect" (default if unset):  reflect the request's Origin header
//   - "*":                             allow any origin (insecure, avoid in prod)
//   - "http://example.com":           allow a specific origin
//   - "" (empty):                     disable CORS entirely (safe behind Nginx)
func corsMiddleware(next http.Handler) http.Handler {
	corsMode := os.Getenv("CORS_ALLOWED_ORIGIN")
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		origin := r.Header.Get("Origin")

		// When CORS_ALLOWED_ORIGIN is unset, reflect the request origin.
		// When set explicitly, use that value (or disable if empty).
		var allowedOrigin string
		switch {
		case corsMode == "reflect" || corsMode == "":
			allowedOrigin = origin
		case corsMode == "*":
			allowedOrigin = "*"
		default:
			allowedOrigin = corsMode
		}

		if allowedOrigin != "" {
			w.Header().Set("Access-Control-Allow-Origin", allowedOrigin)
			w.Header().Set("Vary", "Origin")
		}
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization, Idempotency-Key")

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}