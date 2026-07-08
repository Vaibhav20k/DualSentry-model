package features

type Pipeline struct {
	exporters []Exporter
}

func NewPipeline(exporters ...Exporter) *Pipeline {
	return &Pipeline{
		exporters: exporters,
	}
}

func (p *Pipeline) Process(feature FeatureVector) error {

	for _, exporter := range p.exporters {

		if err := exporter.Export(feature); err != nil {
			return err
		}
	}

	return nil
}