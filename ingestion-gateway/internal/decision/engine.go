package decision

type Decision string

const (
	Allow  Decision = "ALLOW"
	Review Decision = "REVIEW"
	Block  Decision = "BLOCK"
)

type Engine struct {
	reviewThreshold float64
	blockThreshold  float64
}

func NewEngine() *Engine {
	return &Engine{
		reviewThreshold: 0.30,
		blockThreshold:  0.70,
	}
}

func (e *Engine) Decide(
	probability float64,
) Decision {

	switch {

	case probability >= e.blockThreshold:
		return Block

	case probability >= e.reviewThreshold:
		return Review

	default:
		return Allow
	}
}
