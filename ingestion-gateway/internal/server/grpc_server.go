package server

import (
	"fmt"
	"net"

	"google.golang.org/grpc"
)

type GRPCServer struct {
	server *grpc.Server
	port   string
}

func New(port string) *GRPCServer {
	return &GRPCServer{
		server: grpc.NewServer(),
		port:   port,
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
