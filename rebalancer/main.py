"""
Defines the entry point for the Portfolio Rebalancer CLI tool.

This module parses command-line arguments, initializes configuration,
and hands off execution to the appropriate functions.
"""
import argparse
import json
import math
import sys
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


def save_data(file_path: str, data: dict) -> None:
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')


def clear_values(file_path: str) -> None:
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        for asset in data["assets"]:
            asset["current_balance"] = 0.00
        save_data(file_path, data)
    except FileNotFoundError:
        print(f"Error: Portfolio file '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except (json.JSONDecodeError, KeyError, TypeError):
        print(f"Error: Invalid portfolio file '{file_path}'.", file=sys.stderr)
        sys.exit(1)


def apply_values(portfolio: Portfolio, values: list[str]) -> None:
    assets = {asset.name: asset for asset in portfolio.assets}
    names_seen = set()
    for value in values:
        try:
            name, amount = value.split('=', 1)
            amount = float(amount)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid value '{value}'. Use NAME=AMOUNT.")

        name = name.strip()
        if not name or name not in assets:
            raise ValueError(f"Unknown asset in value '{value}'.")
        if not math.isfinite(amount) or amount < 0:
            raise ValueError(f"Value for '{name}' must be a non-negative number.")
        if name in names_seen:
            raise ValueError(f"Value for '{name}' was provided more than once.")
        names_seen.add(name)
        assets[name].current_balance = amount


def save_values(file_path: str, values: list[str]) -> None:
    with open(file_path, 'r') as f:
        data = json.load(f)
    amounts = {value.split('=', 1)[0].strip(): float(value.split('=', 1)[1]) for value in values}
    for asset in data["assets"]:
        if asset["name"] in amounts:
            asset["current_balance"] = amounts[asset["name"]]
    save_data(file_path, data)


def main():
    """The main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="A CLI tool for contribution-only portfolio rebalancing."
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["clear"],
        help="Use 'clear' to reset all current balances to zero."
    )
    parser.add_argument(
        "-c",
        "--contribution",
        type=float, 
        help="The dollar amount you are contributing."
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Optional: Path to your portfolio JSON file. Defaults to 'portfolio.json'."
    )
    parser.add_argument(
        "--value",
        action="append",
        default=[],
        metavar="NAME=AMOUNT",
        help="Override an asset value for this run. Can be used more than once."
    )
    parser.add_argument(
        "--save-values",
        action="store_true",
        help="Save values provided with --value to the portfolio file."
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.4.0"
    )
    args = parser.parse_args()

    if args.command == "clear":
        if args.contribution is not None or args.value or args.save_values:
            parser.error("'clear' cannot be combined with contribution or value options.")
        clear_values(args.file if args.file is not None else DEFAULT_PF_PATH)
        print(f"Cleared current balances in '{args.file if args.file is not None else DEFAULT_PF_PATH}'.")
        return

    if args.contribution is None:
        parser.error("the following arguments are required: -c/--contribution")
    if args.save_values and not args.value:
        parser.error("--save-values requires at least one --value")

    portfolio = load_portfolio(args.file)
    
    try:
        apply_values(portfolio, args.value)
        recommendations = calculate_rebalance(portfolio, args.contribution)
        if args.save_values:
            save_values(args.file if args.file is not None else DEFAULT_PF_PATH, args.value)
        final_total = portfolio.total_value + args.contribution
        
        # Display results
        report_width = 105
        print("\n" + "=" * report_width)
        print("PORTFOLIO REBALANCE REPORT".center(report_width))
        print("=" * report_width)
        print(
            f"{'Asset Class':<20} | {'Current %':>9} | {'Target %':>8} | "
            f"{'Drift':>7} | {'Add':>12} | {'Final %':>8} | {'Final Drift':>11}"
        )
        print("-" * report_width)
        
        for asset in portfolio.assets:
            amount_to_add = recommendations.get(asset.name, 0.0)
            new_balance = asset.current_balance + amount_to_add
            current_alloc = (
                (asset.current_balance / portfolio.total_value) * 100
                if portfolio.total_value > 0
                else 0
            )
            target_alloc = asset.target_allocation * 100
            final_alloc = (new_balance / final_total) * 100 if final_total > 0 else 0
            current_drift = current_alloc - target_alloc
            final_drift = final_alloc - target_alloc
            print(
                f"{asset.name:<20} | {current_alloc:>8.1f}% | "
                f"{target_alloc:>7.1f}% | {current_drift:>+6.1f}% | "
                f"${amount_to_add:>11,.2f} | {final_alloc:>7.1f}% | "
                f"{final_drift:>+10.1f}%"
            )
            
        print("-" * report_width)
        print(f"Total Portfolio Value after contribution: ${final_total:,.2f}")
        print("Status: Rebalancing Complete.\n")
    except ValueError as e:
        print(f"Validation Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
