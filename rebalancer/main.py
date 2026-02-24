"""
Defines the entry point for the Portfolio Rebalancer CLI tool.

This module parses command-line arguments, initializes configuration,
and hands off execution to the appropriate functions.
"""
import argparse
import sys
import json
from .models import Portfolio
from .engine import calculate_rebalance

DEFAULT_PF_PATH = "portfolio.json"

def load_portfolio(file_path: str | None) -> Portfolio:
    """Loads a portfolio from a JSON file, or a default if no path is given."""
    file_to_load = file_path if file_path is not None else DEFAULT_PF_PATH
    
    try:
        with open(file_to_load, 'r') as f:
            data = json.load(f)
            return Portfolio.from_dict(data)
    except FileNotFoundError:
        print(f"\nError: Portfolio file '{file_to_load}' not found.", file=sys.stderr)
        print("\nTo get started:", file=sys.stderr)
        print(f"1. Create a '{file_to_load}' file in your current directory.", file=sys.stderr)
        print("2. Or use the --file flag to point to an existing JSON file.", file=sys.stderr)
        print("\nSee the README for a portfolio.json template.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: The file '{file_to_load}' is not a valid JSON file.", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing expected key {e} in '{file_to_load}'.", file=sys.stderr)
        sys.exit(1)


def main():
    """The main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="A CLI tool for contribution-only portfolio rebalancing."
    )
    parser.add_argument(
        "--contribution", 
        type=float, 
        required=True, 
        help="The dollar amount you are contributing."
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Optional: Path to your portfolio JSON file. Defaults to 'portfolio.json'."
    )
    args = parser.parse_args()

    portfolio = load_portfolio(args.file)
    
    try:
        recommendations = calculate_rebalance(portfolio, args.contribution)
        # Display results
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

if __name__ == "__main__":
    main()
