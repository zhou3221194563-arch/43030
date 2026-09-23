# Cell 2 — Generate true beta
# beta_true is known because this is a controlled synthetic experiment.

rng = np.random.default_rng(SEED)
beta_true = rng.normal(loc=0.0, scale=1.0, size=P)

print("beta_true:")
print(pd.Series(beta_true, index=[f"x{i + 1}" for i in range(P)], name="coefficient"))
