package generator

import (
	"fmt"
	"math/rand"
	"time"

	"github.com/google/uuid"

	"github.com/Vaibhav20k/fintech-pipeline/transaction-simulator/internal/models"
)

var merchants = []struct {
	Name     string
	Category string
}{
	{"Amazon", "ECOMMERCE"},
	{"Flipkart", "ECOMMERCE"},
	{"Swiggy", "FOOD"},
	{"Zomato", "FOOD"},
	{"Uber", "TRANSPORT"},
	{"Ola", "TRANSPORT"},
	{"DMart", "GROCERY"},
	{"Reliance Fresh", "GROCERY"},
	{"Indian Oil", "FUEL"},
	{"HP Petrol", "FUEL"},
}

var paymentMethods = []string{
	"UPI",
	"CARD",
	"NET_BANKING",
}

var cities = []string{
	"Delhi",
	"Noida",
	"Gurgaon",
	"Mumbai",
	"Bangalore",
	"Hyderabad",
}

func Generate() models.Transaction {

	merchant := merchants[rand.Intn(len(merchants))]

	return models.Transaction{

		UserID: uuid.New().String(),

		Timestamp: time.Now().Format(time.RFC3339),

		Amount: float64(rand.Intn(5000) + 100),

		Currency: "INR",

		TransactionType: "PURCHASE",

		PaymentMethod: paymentMethods[rand.Intn(len(paymentMethods))],

		PaymentIdentifier: fmt.Sprintf(
			"user%d@upi",
			rand.Intn(9000)+1000,
		),

		Merchant: merchant.Name,

		MerchantCategory: merchant.Category,

		ReceiverAccount: fmt.Sprintf(
			"ACC%d",
			rand.Intn(999999),
		),

		Location: cities[rand.Intn(len(cities))],

		IPAddress: fmt.Sprintf(
			"192.168.1.%d",
			rand.Intn(255),
		),

		DeviceID: fmt.Sprintf(
			"device_%03d",
			rand.Intn(100),
		),
	}
}