package generator

import (
	"fmt"
	"math"
	"math/rand"
	"time"

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

func Generate() models.Transaction {

	user := RandomUser()

	merchant := merchants[rand.Intn(len(merchants))]

	amount := user.AverageAmount +
		(rand.Float64()*0.4-0.2)*user.AverageAmount

	if amount < 100 {
		amount = 100
	}

	tx := models.Transaction{

		UserID: user.ID,

		Timestamp: time.Now().Format(time.RFC3339),

		Amount: math.Round(amount*100) / 100,

		Currency: "INR",

		TransactionType: "PURCHASE",

		PaymentMethod: user.PreferredPayment,

		PaymentIdentifier: fmt.Sprintf(
			"user_%s@upi",
			user.ID[:8],
		),

		Merchant: merchant.Name,

		MerchantCategory: merchant.Category,

		ReceiverAccount: fmt.Sprintf(
			"ACC%d",
			rand.Intn(999999),
		),

		Location: user.HomeCity,

		IPAddress: user.IPAddress,

		DeviceID: user.DeviceID,
	}

	InjectFraud(&tx)

	return tx

}
