"""Implements the core math to calculate the recommended contribution amounts."""
from typing import Dict
from .models import Portfolio

def calculate_rebalance(portfolio: Portfolio, contribution: float) -> Dict[str, float]:
    """
    Calculates how to distribute a contribution across assets to reach target allocations.
    
    Logic:
    1. Calculate the 'Ideal' total value after contribution.
    2. Calculate the 'Target Amount' for each asset based on its target %.
    3. Calculate the 'Gap' (Target Amount - Current Balance).
    4. If the contribution is less than the total gap, distribute it 
       proportionally to those gaps.
    """
    if not portfolio.validate():
        raise ValueError("Portfolio target allocations must sum to 1.0 (100%).")

    if contribution < 0:
        raise ValueError("Contribution must be a positive number.")

    new_total_value = portfolio.total_value + contribution
    
    # Calculate how much we want to add to each to hit the target
    gaps = {}
    for asset in portfolio.assets:
        target_amount = new_total_value * asset.target_allocation
        gap = target_amount - asset.current_balance
        gaps[asset.name] = max(0.0, gap) # Ignore negative gaps (sells)

    total_gap = sum(gaps.values())
   
    # If no contribution calculated, return zeros immediately. 
    # This is to avoid division by 0 later.
    if total_gap == 0:
        return {asset.name: 0.0 for asset in portfolio.assets}

    # If contribution != total_gap, we scale the additions.
    scaling_factor = contribution / total_gap

    result = {}
    for name, gap in gaps.items():
        result[name] = round(gap * scaling_factor, 2)
    return result
