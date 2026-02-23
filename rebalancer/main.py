import argparse
import sys
from .models import AssetClass, Portfolio
from .engine import calculate_rebalance

def main():
    """
    The main entry point for the CLI.
    This function handles parsing arguments, running the logic, 
    and printing the results in a clean format.
    """
    parser = argparse.ArgumentParser(
        description="Portfolio Rebalancer: Calculate contribution-only rebalancing."
    )

    parser.add_argument(
        "--contribution", 
        type=float, 
        required=True, 
        help="The dollar amount you are contributing today."
    )

    args = parser.parse_args()

    # A convenient demo portfolio to be run by default TODO
    demo_portfolio = [
        AssetClass("US Total Stock", 0.60, 6000.0),
        AssetClass("Intl Stock", 0.30, 2000.0),
        AssetClass("Bond Market", 0.10, 2000.0),
    ]
    portfolio = Portfolio(demo_portfolio)

    try:
        recommendations = calculate_rebalance(portfolio, args.contribution)

        print("\n" + "="*40)
        print("     PORTFOLIO REBALANCE REPORT")
        print("="*40)
        print(f"Current Value:  ${portfolio.total_value:,.2f}")
        print(f"Contribution:   ${args.contribution:,.2f}")
        print("-" * 40)
        
        for name, amount in recommendations.items():
            print(f"{name:<20}: ${amount:>12,.2f}")
        
        print("-" * 40)
        print("Status: Rebalancing Complete.\n")

    except ValueError as e:
        print(f"Validation Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
