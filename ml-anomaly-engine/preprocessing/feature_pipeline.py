from __future__ import annotations

from collections import defaultdict

import pandas as pd

from preprocessing.account_state import AccountState


class FeaturePipeline:

    def __init__(self):

        self.account_states: dict[
            str,
            AccountState,
        ] = defaultdict(
            lambda: AccountState("")
        )

    def process_transaction(
        self,
        row: pd.Series,
    ) -> dict:

        account = str(
            row["Account"]
        )

        state = self.account_states[
            account
        ]

        sender_bank = int(
            row["From Bank"]
        )

        receiver_bank = int(
            row["To Bank"]
        )

        payment_currency = str(
            row["Payment Currency"]
        )

        receiving_currency = str(
            row["Receiving Currency"]
        )

        if state.account_id == "":

            state.account_id = account

        timestamp = pd.to_datetime(
            row["Timestamp"],
            errors="coerce",
        )

        amount = float(
            row.get(
                "Amount Paid",
                0.0,
            )
        )

        receiver = str(
            row["Account.1"]
        )

        payment = str(
            row["Payment Format"]
        )

        feature_vector = {

            "amount": amount,

            "payment_channel": payment,

            "time_since_last_transaction":
                state.time_since_last(
                    timestamp,
                ),

            "velocity_score":
                state.velocity_score(),

            "spending_deviation_score":
                state.spending_zscore(
                    amount,
                ),

            "is_first_transaction":
                int(
                    state.is_first_transaction()
                ),

            "hour":
                timestamp.hour,

            "day_of_week":
                timestamp.dayofweek,

            "month":
                timestamp.month,

            "is_weekend":
                int(
                    timestamp.dayofweek >= 5
                ),

            "is_fraud":
                int(
                    row["Is Laundering"]
                ),

            "is_cross_bank_transfer":
                int(
                    sender_bank != receiver_bank
                ),

            "is_cross_currency_transfer":
                int(
                    payment_currency != receiving_currency
                ),

            "is_new_receiver":
                int(
                    state.is_new_receiver(
                        receiver,
                    )
                ),
            
            "is_new_bank":
                int(
                    state.is_new_bank(
                        receiver_bank,
                    )
                ),

            "is_new_payment_format":
                int(
                    payment
                    not in
                    state.known_payment_formats
                ),
                    }

        state.update_after_transaction(

            amount=amount,

            timestamp=timestamp,

            receiver=receiver,

            payment_format=payment,

            bank=sender_bank,

            currency=payment_currency,
        )

        return feature_vector
    
    def process_dataframe(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = df.sort_values(
            [
                "Account",
                "Timestamp",
            ]
        )

        features = []

        for _, row in df.iterrows():

            features.append(
                self.process_transaction(
                    row,
                )
            )

        return pd.DataFrame(
            features,
        )