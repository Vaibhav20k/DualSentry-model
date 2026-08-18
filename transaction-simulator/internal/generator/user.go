package generator

import (
	"fmt"
	"math/rand"

	"github.com/google/uuid"

	"github.com/Vaibhav20k/fintech-pipeline/transaction-simulator/internal/models"
)

var homeCities = []string{
	"Delhi",
	"Noida",
	"Gurgaon",
	"Mumbai",
	"Bangalore",
	"Hyderabad",
}

var paymentPrefs = []string{
	"UPI",
	"CARD",
	"NET_BANKING",
}

var favoriteMerchants = []string{
	"Amazon",
	"Flipkart",
	"Swiggy",
	"Zomato",
	"Uber",
	"Ola",
	"DMart",
	"Reliance Fresh",
	"Indian Oil",
	"HP Petrol",
}

var users []models.UserProfile

func InitUsers(count int) {

	users = make([]models.UserProfile, 0, count)

	for i := 0; i < count; i++ {

		users = append(users, models.UserProfile{

			ID: uuid.New().String(),

			HomeCity: homeCities[rand.Intn(len(homeCities))],

			PreferredPayment: paymentPrefs[rand.Intn(len(paymentPrefs))],

			FavoriteMerchant: favoriteMerchants[rand.Intn(len(favoriteMerchants))],

			AverageAmount: float64(rand.Intn(4000) + 500),

			DeviceID: fmt.Sprintf(
				"device_%04d",
				i,
			),

			IPAddress: fmt.Sprintf(
				"192.168.1.%d",
				(i%254)+1,
			),

			ActiveStartHour: 8,

			ActiveEndHour: 22,
		})
	}
}

func RandomUser() models.UserProfile {

	return users[rand.Intn(len(users))]
}
