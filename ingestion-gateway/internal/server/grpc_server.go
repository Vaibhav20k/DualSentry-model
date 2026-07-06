package server

import (
	"fmt"
	"net"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/config"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/handler"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/kafka"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/postgres"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/service"

	pb "github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/proto"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

type GRPCServer struct {
	server *grpc.Server
	port   string
}

func New(cfg *config.Config) *GRPCServer {

	grpcServer := grpc.NewServer()

	// PostgreSQL Connection
	db, err := postgres.NewConnection(cfg)
	if err != nil {
		panic(err)
	}

	// Repository
	repo := postgres.NewTransactionRepository(db)

	// Kafka Producer
	producer, err := kafka.NewProducer(cfg.KafkaBrokers,cfg.KafkaTopic)
	if err != nil {
		panic(err)
	}

	// Service
	svc := service.NewTransactionService(repo, producer)

	// Handler
	transactionHandler := handler.NewTransactionHandler(svc)

	pb.RegisterTransactionServiceServer(
		grpcServer,
		transactionHandler,
	)

	reflection.Register(grpcServer)

	return &GRPCServer{
		server: grpcServer,
		port:   cfg.ServerPort,
	}
}

func (g *GRPCServer) Start() error {

	lis, err := net.Listen("tcp", ":"+g.port)
	if err != nil {
		return fmt.Errorf("failed to listen on port %s: %w", g.port, err)
	}

	fmt.Printf("🚀 gRPC Server listening on port %s\n", g.port)

	return g.server.Serve(lis)
}

func (g *GRPCServer) Stop() {
	g.server.GracefulStop()
}