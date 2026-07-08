package features

type Exporter interface {
	Export(FeatureVector) error
}