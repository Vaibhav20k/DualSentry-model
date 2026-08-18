package decision_test

import (
	"fmt"
	"testing"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/decision"
)

func TestDecisionEngineAllBoundaries(t *testing.T) {
	eng := decision.NewEngine()

	tests := []struct {
		probability float64
		expected    decision.Decision
	}{
		{0.00, decision.Allow},
		{0.10, decision.Allow},
		{0.29, decision.Allow},
		{0.30, decision.Review},
		{0.31, decision.Review},
		{0.50, decision.Review},
		{0.69, decision.Review},
		{0.70, decision.Block},
		{0.71, decision.Block},
		{0.90, decision.Block},
		{0.9842, decision.Block},
		{0.9843, decision.Block},
		{0.9844, decision.Block},
		{1.00, decision.Block},
	}

	for _, tt := range tests {
		name := fmt.Sprintf("prob_%.4f", tt.probability)
		t.Run(name, func(t *testing.T) {
			got := eng.Decide(tt.probability)
			if got != tt.expected {
				t.Errorf("Decide(%f) = %v, want %v", tt.probability, got, tt.expected)
			}
		})
	}
}
