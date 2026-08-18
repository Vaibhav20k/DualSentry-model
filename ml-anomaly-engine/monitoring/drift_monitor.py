from collections import Counter


class DriftMonitor:
    """
    Tracks live feature statistics and compares them against
    training statistics stored in model metadata.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.total_predictions = 0

        self.total_amount = 0.0
        self.total_velocity = 0.0
        self.total_spending_deviation = 0.0

        self.payment_channel_counter = Counter()

    def update(self, transaction: dict):
        self.total_predictions += 1

        self.total_amount += transaction["amount"]
        self.total_velocity += transaction["velocity_score"]
        self.total_spending_deviation += transaction["spending_deviation_score"]

        self.payment_channel_counter[
            transaction["payment_channel"]
        ] += 1

    def current_statistics(self):

        if self.total_predictions == 0:
            return {
                "samples": 0,
                "average_amount": 0,
                "average_velocity_score": 0,
                "average_spending_deviation": 0,
                "payment_channel_distribution": {}
            }

        distribution = {
            channel: round(
                count / self.total_predictions,
                4
            )
            for channel, count in self.payment_channel_counter.items()
        }

        return {
            "samples": self.total_predictions,
            "average_amount": round(
                self.total_amount / self.total_predictions,
                2,
            ),
            "average_velocity_score": round(
                self.total_velocity / self.total_predictions,
                4,
            ),
            "average_spending_deviation": round(
                self.total_spending_deviation /
                self.total_predictions,
                4,
            ),
            "payment_channel_distribution": distribution,
        }

    def detect_drift(self, metadata: dict):

        current = self.current_statistics()

        training = metadata.get(
            "training_stats",
            {}
        )

        if current["samples"] == 0:
            return {
                "drift_detected": False,
                "severity": "NONE",
                "drift_score": 0.0,
                "live_statistics": current,
                "training_statistics": training,
            }

        score = 0.0

        comparisons = 0

        def compare(live, train):

            if train == 0:
                return 0

            return abs(live - train) / abs(train)

        if "mean_amount" in training and training["mean_amount"] != 0:
            score += compare(
                current["average_amount"],
                training["mean_amount"],
            )
            comparisons += 1

        if comparisons == 0:
            drift_score = 0.0
        else:
            drift_score = round(
                score / comparisons,
                4,
            )

        if drift_score < 0.10:

            severity = "LOW"

        elif drift_score < 0.25:

            severity = "MEDIUM"

        else:

            severity = "HIGH"

        return {

            "drift_detected": drift_score >= 0.25,

            "severity": severity,

            "drift_score": drift_score,

            "live_statistics": current,

            "training_statistics": training,
        }