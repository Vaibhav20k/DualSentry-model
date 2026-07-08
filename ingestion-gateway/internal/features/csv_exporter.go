package features

import (
	"encoding/csv"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

type CSVExporter struct {
	filePath string
}

func NewCSVExporter(filePath string) *CSVExporter {
	return &CSVExporter{
		filePath: filePath,
	}
}

func (e *CSVExporter) Export(feature FeatureVector) error {

	// Create directory if it doesn't exist.
	if err := os.MkdirAll(filepath.Dir(e.filePath), os.ModePerm); err != nil {
		return err
	}

	// Check whether file already exists.
	_, err := os.Stat(e.filePath)
	fileExists := err == nil

	file, err := os.OpenFile(
		e.filePath,
		os.O_CREATE|os.O_APPEND|os.O_WRONLY,
		0644,
	)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// Write header only once.
	if !fileExists {

		header := []string{
			"TransactionID",
			"UserID",
			"Amount",
			"AmountDeviation",
			"AmountZScore",
			"TransactionVelocity1H",
			"HourOfDay",
			"DayOfWeek",
			"IsWeekend",
			"OutsideActiveHours",
			"NewMerchant",
			"NewDevice",
			"NewLocation",
			"PaymentMethodChanged",
			"MerchantFrequency",
			"DeviceTrustScore",
			"MerchantTrustScore",
			"LocationRiskScore",
			"TimeSinceLastTransaction",
			"RiskFlags",
		}

		if err := writer.Write(header); err != nil {
			return err
		}
	}

	record := []string{
		feature.TransactionID,
		feature.UserID,
		strconv.FormatFloat(feature.Amount, 'f', -1, 64),
		strconv.FormatFloat(feature.AmountDeviation, 'f', -1, 64),
		strconv.FormatFloat(feature.AmountZScore, 'f', -1, 64),
		strconv.Itoa(feature.TransactionVelocity1H),
		strconv.Itoa(feature.HourOfDay),
		strconv.Itoa(feature.DayOfWeek),
		strconv.FormatBool(feature.IsWeekend),
		strconv.FormatBool(feature.OutsideActiveHours),
		strconv.FormatBool(feature.NewMerchant),
		strconv.FormatBool(feature.NewDevice),
		strconv.FormatBool(feature.NewLocation),
		strconv.FormatBool(feature.PaymentMethodChanged),
		strconv.FormatFloat(feature.MerchantFrequency, 'f', -1, 64),
		strconv.FormatFloat(feature.DeviceTrustScore, 'f', -1, 64),
		strconv.FormatFloat(feature.MerchantTrustScore, 'f', -1, 64),
		strconv.FormatFloat(feature.LocationRiskScore, 'f', -1, 64),
		strconv.FormatFloat(feature.TimeSinceLastTransaction, 'f', -1, 64),
		strings.Join(feature.RiskFlags, "|"),
	}

	if err := writer.Write(record); err != nil {
		return err
	}

	writer.Flush()

	return writer.Error()
}