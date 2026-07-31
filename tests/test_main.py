import json

import pytest

from rebalancer.main import main


def write_portfolio(path):
    path.write_text(json.dumps({
        "assets": [
            {"name": "A", "target_allocation": 0.5, "current_balance": 100.0},
            {"name": "B", "target_allocation": 0.5, "current_balance": 100.0},
        ]
    }))


def test_clear_values_keeps_portfolio_structure(tmp_path, monkeypatch):
    path = tmp_path / "portfolio.json"
    write_portfolio(path)
    monkeypatch.setattr("sys.argv", ["rebalance", "clear", "--file", str(path)])

    main()

    data = json.loads(path.read_text())
    assert data["assets"][0]["current_balance"] == 0.0
    assert data["assets"][0]["target_allocation"] == 0.5


def test_value_overrides_are_used_without_saving(tmp_path, monkeypatch, capsys):
    path = tmp_path / "portfolio.json"
    write_portfolio(path)
    monkeypatch.setattr(
        "sys.argv",
        ["rebalance", "-c", "10", "--file", str(path), "--value", "A=0"],
    )

    main()

    assert "A" in capsys.readouterr().out
    assert json.loads(path.read_text())["assets"][0]["current_balance"] == 100.0


def test_value_overrides_can_be_saved(tmp_path, monkeypatch):
    path = tmp_path / "portfolio.json"
    write_portfolio(path)
    monkeypatch.setattr(
        "sys.argv",
        [
            "rebalance", "-c", "10", "--file", str(path),
            "--value", "A=0", "--save-values",
        ],
    )

    main()

    assert json.loads(path.read_text())["assets"][0]["current_balance"] == 0.0


def test_unknown_value_asset_is_rejected(tmp_path, monkeypatch):
    path = tmp_path / "portfolio.json"
    write_portfolio(path)
    monkeypatch.setattr(
        "sys.argv",
        ["rebalance", "-c", "10", "--file", str(path), "--value", "C=0"],
    )

    with pytest.raises(SystemExit):
        main()
