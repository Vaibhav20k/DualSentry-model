from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AccountState:
    """
    Running behavioural profile of a sender account.

    IMPORTANT:
    This state only contains information from
    PREVIOUS transactions.

    After features are generated,
    the state is updated.
    """

    account_id: str

    transaction_count: int = 0

    total_amount: float = 0.0

    mean_amount: float = 0.0

    m2_amount: float = 0.0

    last_timestamp: datetime | None = None

    last_bank: str | None = None

    known_receivers: set[str] = field(default_factory=set)

    known_payment_formats: set[str] = field(default_factory=set)

    known_banks: set[int] = field(
    default_factory=set,
    )

    known_currencies: set[str] = field(
        default_factory=set,
    )


    def update_amount_statistics(
        self,
        amount: float,
    ) -> None:
        """
        Online update of mean and variance.

        Uses Welford's Algorithm.
        """

        self.transaction_count += 1

        delta = amount - self.mean_amount

        self.mean_amount += (
            delta / self.transaction_count
        )

        delta2 = amount - self.mean_amount

        self.m2_amount += (
            delta * delta2
        )

        self.total_amount += amount


    @property
    def std_amount(
        self,
    ) -> float:

        if self.transaction_count < 2:
            return 1.0

        variance = (
            self.m2_amount
            /
            (self.transaction_count - 1)
        )

        return max(
            variance ** 0.5,
            1.0,
        )
    def spending_zscore(
        self,
        amount: float,
    ) -> float:

        if self.transaction_count < 2:
            return 0.0

        return (
            amount - self.mean_amount
        ) / self.std_amount

        return (
            amount - self.mean_amount
        ) / self.std_amount

    def time_since_last(
        self,
        timestamp: datetime,
    ) -> float:

        if self.last_timestamp is None:
            return 0.0

        return (
            timestamp -
            self.last_timestamp
        ).total_seconds()

    def velocity_score(
        self,
    ) -> int:

        return self.transaction_count

    def is_first_transaction(
        self,
    ) -> bool:

        return self.transaction_count == 0

    def is_new_receiver(
        self,
        receiver: str,
    ) -> bool:

        return (
            receiver
            not in self.known_receivers
        )

    def is_new_bank(
        self,
        bank: int,
    ) -> bool:

        return (
            bank
            not in self.known_banks
        )

    def update_after_transaction(
        self,
        amount: float,
        timestamp: datetime,
        receiver: str,
        payment_format: str,
        bank: int,
        currency: str,
    ) -> None:

        self.update_amount_statistics(
            amount,
        )

        self.last_timestamp = timestamp

        self.known_receivers.add(
            receiver,
        )

        self.known_payment_formats.add(
            payment_format,
        )

        self.known_banks.add(
            bank,
        )

        self.known_currencies.add(
            currency,
        )