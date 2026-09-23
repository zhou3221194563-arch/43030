# Cell 1 — Imports and configuration
# Run this cell first. Change experiment settings only in this cell.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

SEED = 42
N_TRAIN = 500
N_VAL = 200
N_TEST = 1000
P = 10
NOISE_STD = 1.0
CONTAMINATION_RATIO = 0.10
CONTAMINATION_MAGNITUDE = 5.0
CONTAMINATION_TYPE = "response"  # "response" or "cellwise"

# Benchmark grid. The single experiment above is shown before this grid runs.
BENCHMARK_DIMENSIONS = [5, 10, 20, 40]
BENCHMARK_RATIOS = [0.00, 0.05, 0.10, 0.20, 0.30]
BENCHMARK_MAGNITUDES = [2.0, 5.0, 10.0]
BENCHMARK_TYPES = ["response", "cellwise"]
BENCHMARK_REPEATS = 20

if CONTAMINATION_TYPE not in {"response", "cellwise"}:
    raise ValueError("CONTAMINATION_TYPE must be 'response' or 'cellwise'.")
if not 0.0 <= CONTAMINATION_RATIO <= 1.0:
    raise ValueError("CONTAMINATION_RATIO must be between 0 and 1.")

pd.set_option("display.precision", 3)
plt.style.use("seaborn-v0_8-whitegrid")
