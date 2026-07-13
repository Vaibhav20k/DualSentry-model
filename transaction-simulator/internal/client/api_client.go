package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/Vaibhav20k/fintech-pipeline/transaction-simulator/internal/models"
)

type APIClient struct {
	baseURL string
	client  *http.Client
}

func New(baseURL string) *APIClient {
	return &APIClient{
		baseURL: baseURL,
		client:  &http.Client{},
	}
}

func (c *APIClient) SendTransaction(
	transaction models.Transaction,
) error {

	body, err := json.Marshal(transaction)
	if err != nil {
		return err
	}

	resp, err := c.client.Post(
		c.baseURL+"/api/transactions",
		"application/json",
		bytes.NewBuffer(body),
	)
	if err != nil {
		return err
	}

	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK &&
		resp.StatusCode != http.StatusCreated {

		return fmt.Errorf(
			"API returned status %d",
			resp.StatusCode,
		)
	}

	return nil
}