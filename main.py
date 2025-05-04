from strategies.momentum_composite import MomentumComposite

if __name__ == "__main__":
    config = {
        "universe": "nifty500",
        "start_date": "2018-12-01",           # for indicator warm-up
        "backtest_start_date": "2020-01-01",  # actual backtest start
        "initial_capital": 1_000_000,  # 💰 Starting portfolio value
        "force_refresh": False
    }

    strategy = MomentumComposite(config)

    # Run dummy backtest to test BacktestResult
    strategy.backtest(top_n=20, rebalance_frequency="W")
