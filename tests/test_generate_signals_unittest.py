import unittest
import pandas as pd
from strategy import generate_signals


class TestGenerateSignals(unittest.TestCase):
    def test_signal_column(self):
        df = pd.DataFrame(
            {
                "Close": list(range(1, 30)),
                "PE_Ratio": [15] * 29,
            }
        )
        result = generate_signals(df.copy())
        self.assertIn("signal", result.columns)
        self.assertEqual(result.shape[0], df.shape[0])
        self.assertTrue((result["signal"] != 0).any())


if __name__ == "__main__":
    unittest.main()
