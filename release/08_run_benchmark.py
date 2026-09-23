# Cell 8 — Run benchmark over predefined parameter grids
# This helper repeats the already-shown single-experiment workflow. It does not
# replace the visible top-level workflow in cells 2–7.

def run_benchmark_experiment(p, ratio, magnitude, contamination_type, seed):
    generator = np.random.default_rng(seed)
    beta = generator.normal(0.0, 1.0, size=p)
    X_train, y_train = generate_clean_set(N_TRAIN, beta, NOISE_STD, generator)
    X_validation, y_validation = generate_clean_set(N_VAL, beta, NOISE_STD, generator)
    X_testing, y_testing = generate_clean_set(N_TEST, beta, NOISE_STD, generator)
    X_observed, y_observed, _, _ = inject_contamination(
        X_train, y_train, contamination_type, ratio, magnitude, NOISE_STD, generator
    )
    X_design = add_intercept(X_observed)
    theta = np.linalg.solve(X_design.T @ X_design, X_design.T @ y_observed)
    validation = regression_metrics(X_validation, y_validation, theta, beta)
    testing = regression_metrics(X_testing, y_testing, theta, beta)
    return {
        "p": p,
        "contamination_ratio": ratio,
        "contamination_magnitude": magnitude,
        "contamination_type": contamination_type,
        "seed": seed,
        "clean_validation_MSE": validation["MSE"],
        "clean_test_MSE": testing["MSE"],
        "parameter_L2_error": testing["parameter_L2_error"],
    }


benchmark_records = []
for p_value in BENCHMARK_DIMENSIONS:
    for ratio_value in BENCHMARK_RATIOS:
        for magnitude_value in BENCHMARK_MAGNITUDES:
            for type_value in BENCHMARK_TYPES:
                for repeat in range(BENCHMARK_REPEATS):
                    benchmark_seed = SEED + 10_000 * repeat + 100 * p_value + int(1_000 * ratio_value) + int(magnitude_value)
                    benchmark_records.append(
                        run_benchmark_experiment(p_value, ratio_value, magnitude_value, type_value, benchmark_seed)
                    )

benchmark_results = pd.DataFrame(benchmark_records)
print(f"completed {len(benchmark_results)} benchmark runs")
