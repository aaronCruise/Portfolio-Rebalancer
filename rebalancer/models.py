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

    def validate(self) -> bool:
        """Ensures the portfolio is valid in that the target allocations sum to 100%."""
        total_allocation = sum(asset.target_allocation for asset in self.assets)
        # Using round to account for floating point math quirks
        return round(total_allocation, 4) == 1.0

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
