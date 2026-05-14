"""Test suite to verify the math implementation in engine.py"""
import pytest
from rebalancer.models import AssetClass, Portfolio
from rebalancer.engine import calculate_rebalance

def test_calculate_rebalance_perfect_fit():
    """
    Test case: We have enough contribution to reach the exact target.
    Portfolio: $900 total. Target: 50/50 ($500/$500).
    Current: A=$400, B=$500. 
    Contribution: $100.
    Expected: Add $100 to A, $0 to B.
    """
    # Arrange
    a = AssetClass("A", 0.5, 400.0)
    b = AssetClass("B", 0.5, 500.0)
    portfolio = Portfolio([a, b])
    contribution = 100.0

    # Act
    result = calculate_rebalance(portfolio, contribution)

    # Assert
    assert result["A"] == 100.0
    assert result["B"] == 0.0

def test_calculate_rebalance_proportional_scaling():
    """
    Test case: Contribution is NOT enough to fill the gap.
    Portfolio: $800 total. Target: 50/50 ($400/$400)
    Current: A=$400, B=$400.
    Contribution: $50.
    Expected: Both get 50% of their gap ($25 each).
    """
    # Arrange
    a = AssetClass("A", 0.5, 400.0) 
    b = AssetClass("B", 0.5, 400.0)
    portfolio = Portfolio([a, b])
    contribution = 50.0

    # Act
    result = calculate_rebalance(portfolio, contribution)

    # Assert
    assert result["A"] == 25.0
    assert result["B"] == 25.0

def test_zero_contribution():
    """
    Test case: Contribution is $0.
    Portfolio: $800 total. Target: 50/50 ($400/$400)
    Current: A=$400, B=$400.
    Contribution: $0
    Expected: Add $0 each.
    """
    # Arrange
    a = AssetClass("A", 0.5, 400.0) 
    b = AssetClass("B", 0.5, 400.0)
    portfolio = Portfolio([a, b])
    contribution = 0.0

    # Act
    result = calculate_rebalance(portfolio, contribution)

    # Assert
    assert result["A"] == 0.0
    assert result["B"] == 0.0

def test_invalid_contribution_raises_error():
    """
    Test case: Negative contribution should raise a ValueError.
    """
    portfolio = Portfolio([AssetClass("A", 1.0, 100.0)])

    with pytest.raises(ValueError, match="Contribution must be a positive number"):
        calculate_rebalance(portfolio, -100.0)

def test_empty_portfolio_raises_error():
    """Test case: A portfolio must include at least one asset."""
    portfolio = Portfolio([])

    with pytest.raises(ValueError, match="at least one asset"):
        calculate_rebalance(portfolio, 100.0)

def test_invalid_target_allocation_total_raises_error():
    """Test case: Target allocations must sum to 100%."""
    portfolio = Portfolio(
        [
            AssetClass("A", 0.5, 100.0),
            AssetClass("B", 0.4, 100.0),
        ]
    )

    with pytest.raises(ValueError, match="allocations must sum to 1.0"):
        calculate_rebalance(portfolio, 100.0)

def test_negative_asset_values_raise_error():
    """Test case: Asset balances and target allocations cannot be negative."""
    portfolio = Portfolio(
        [
            AssetClass("A", 1.1, 100.0),
            AssetClass("B", -0.1, -50.0),
        ]
    )

    with pytest.raises(ValueError, match="cannot be negative"):
        calculate_rebalance(portfolio, 100.0)

def test_duplicate_asset_names_raise_error():
    """Test case: Asset names must be unique."""
    portfolio = Portfolio(
        [
            AssetClass("A", 0.5, 100.0),
            AssetClass("A", 0.5, 100.0),
        ]
    )

    with pytest.raises(ValueError, match="duplicated"):
        calculate_rebalance(portfolio, 100.0)

def test_empty_asset_names_raise_error():
    """Test case: Asset names cannot be blank."""
    portfolio = Portfolio([AssetClass(" ", 1.0, 100.0)])

    with pytest.raises(ValueError, match="cannot be empty"):
        calculate_rebalance(portfolio, 100.0)
