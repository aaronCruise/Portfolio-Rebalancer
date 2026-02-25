# Portfolio Rebalancer

A CLI tool designed to help investors maintain their target asset allocation through contribution-only rebalancing.

<p align="center">
  <a href="https://badge.fury.io/py/portfolio-rebalancer-cli"><img src="https://badge.fury.io/py/portfolio-rebalancer-cli.svg" alt="PyPI version"></a>
  <a href="https://www.python.org/downloads/release/python-3100/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/aaronCruise/Portfolio-Rebalancer/refs/heads/main/images/output_example.png" alt="output_example"/>
</p>

This project was built using **Gemini CLI** to explore AI-driven development for architectural designs, scaffolding, and code generation.

## Motivation
I originally managed my investments and rebalancing through a spreadsheet. I ported the logic to a CLI tool to achieve:
- Workflow efficiency. Faster execution and a foundation for future automation.
- Version control. My investment strategy and portfolio can now be tracked with Git.
- Reliability. All logic lies within modules that are invisible to the user. No more accidental formula breaks!

## Features
- **Tax-Efficient Logic:** Prioritizes buying underweight assets, never selling.
- **JSON Portfolios:** Load your custom portfolio from a simple `json` file.
- **Proportional Scaling:** Handles contributions that are too small to fill all gaps perfectly.
- **Modern Python:** Built with type hints, dataclasses, and a modular package structure.

## Installation

Install the tool directly from PyPI:

```bash
pip install portfolio-rebalancer-cli
```

## Usage 

1. **Configure your portfolio:**
   Create a `portfolio.json` file in your current directory using the following format, adding asset classes and adjusting according to your portfolio:

    ```json
    {
      "assets": [
        {
          "name": "US Total Stock",
          "target_allocation": 0.60,
          "current_balance": 6000.00
        },
        {
          "name": "International Stock",
          "target_allocation": 0.30,
          "current_balance": 2000.00
        },
        {
          "name": "Bond Market",
          "target_allocation": 0.10,
          "current_balance": 2000.00
        }
      ]
    }
    ```

2. **Run the rebalancer:**

    * **Default Mode** (looks for `portfolio.json` in current folder):
      ```bash
      rebalance --contribution 1000
      ```

    * **Custom File Mode**:
      ```bash
      rebalance --contribution 1000 --file my_custom_portfolio.json
      ```

## Development & Testing

If you want to contribute or run the tests:

```bash
git clone https://github.com/aaronCruise/Portfolio-Rebalancer.git
cd Portfolio-Rebalancer
pip install -e .
pytest
```
