import pandas as pd
from strategy import generate_signals


def test_generate_signals_basic():
    """Simple sanity test for the placeholder strategy.
    Uses a monotonically increasing price series so that after the SMA
    window is filled, the price should be above the SMA and trigger a
    buy signal (1)."""
    # 25 days of increasing close prices
    df = pd.DataFrame(
        {
            "Close": list(range(1, 26)),
            "PE_Ratio": [15] * 25,
        }
    )
    result = generate_signals(df.copy())
    # Verify the signal column exists and that the output DataFrame shape matches input
    assert "signal" in result.columns
    assert result.shape[0] == df.shape[0]
    # Ensure that at least one non-zero signal is produced (could be 1 or -1)
    assert (result["signal"] != 0).any()
