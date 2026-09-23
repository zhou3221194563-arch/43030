# Cell 9 — Produce tables and plots

benchmark_summary = (
    benchmark_results.groupby(
        ["p", "contamination_ratio", "contamination_magnitude", "contamination_type"], as_index=False
    )
    .agg(
        mean_clean_test_MSE=("clean_test_MSE", "mean"),
        std_clean_test_MSE=("clean_test_MSE", "std"),
        mean_parameter_L2_error=("parameter_L2_error", "mean"),
        std_parameter_L2_error=("parameter_L2_error", "std"),
    )
    .sort_values(["contamination_type", "p", "contamination_magnitude", "contamination_ratio"])
)

display(benchmark_summary)

# Plot the middle predefined magnitude; edit BENCHMARK_MAGNITUDES in cell 1 to change it.
plot_magnitude = BENCHMARK_MAGNITUDES[len(BENCHMARK_MAGNITUDES) // 2]
plot_data = benchmark_summary[benchmark_summary["contamination_magnitude"] == plot_magnitude]

fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharex=True)
for contamination_type, type_data in plot_data.groupby("contamination_type"):
    for p_value, p_data in type_data.groupby("p"):
        label = f"{contamination_type}, p={p_value}"
        axes[0].plot(p_data["contamination_ratio"], p_data["mean_parameter_L2_error"], marker="o", label=label)
        axes[1].plot(p_data["contamination_ratio"], p_data["mean_clean_test_MSE"], marker="o", label=label)

axes[0].set(title="Parameter error vs contamination ratio", xlabel="contamination ratio", ylabel="mean L2 parameter error")
axes[1].set(title="Clean-test MSE vs contamination ratio", xlabel="contamination ratio", ylabel="mean clean-test MSE")
for axis in axes:
    axis.legend(fontsize=8)
fig.suptitle(f"Contamination magnitude = {plot_magnitude}")
fig.tight_layout()
plt.show()
