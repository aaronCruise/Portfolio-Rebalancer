"""Defines the classes to represent a portfolio and its components."""
from dataclasses import dataclass, field

@dataclass
class AssetClass:
    name: str
    target_allocation: float  # As a decimal (ex, 0.60 for 60%)
    current_balance: float

@dataclass
class Portfolio:
    assets: list[AssetClass] = field(default_factory=list)

    @property
    def total_value(self) -> float:
        """Calculates the total value across all asset classes."""
        return sum(asset.current_balance for asset in self.assets)

    def validation_errors(self) -> list[str]:
        """Returns validation errors for portfolio structure and asset values."""
        errors = []
        if not self.assets:
            errors.append("Portfolio must include at least one asset.")

        names_seen = set()
        for asset in self.assets:
            if not asset.name.strip():
                errors.append("Asset names cannot be empty.")
            elif asset.name in names_seen:
                errors.append(f"Asset name '{asset.name}' is duplicated.")
            names_seen.add(asset.name)

            if asset.target_allocation < 0:
                errors.append(
                    f"Asset '{asset.name}' target allocation cannot be negative."
                )
            if asset.current_balance < 0:
                errors.append(f"Asset '{asset.name}' balance cannot be negative.")

        total_allocation = sum(asset.target_allocation for asset in self.assets)
        if round(total_allocation, 4) != 1.0:
            errors.append("Portfolio target allocations must sum to 1.0 (100%).")

        return errors

    def validate(self) -> bool:
        """Ensures the portfolio has valid assets and target allocations."""
        return not self.validation_errors()

    @classmethod
    def from_dict(cls, data: dict) -> "Portfolio":
        """Creates a Portfolio instance from a dictionary."""
        assets = []
        for dict_item in data.get("assets", []):
            assets.append(
                AssetClass(
                    name=dict_item["name"],
                    target_allocation=dict_item["target_allocation"],
                    current_balance=dict_item["current_balance"]
                )
            )
        return cls(assets=assets)
