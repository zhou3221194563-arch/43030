# Cell 3 — Generate clean train / validation / test sets
# Each split is independently generated. Only the training split is contaminated later.

def generate_clean_set(n_samples, beta, noise_std, generator):
    """Return X and y from y = X @ beta + Normal(0, noise_std)."""
    X = generator.normal(loc=0.0, scale=1.0, size=(n_samples, len(beta)))
    noise = generator.normal(loc=0.0, scale=noise_std, size=n_samples)
    y = X @ beta + noise
    return X, y


X_train_clean, y_train_clean = generate_clean_set(N_TRAIN, beta_true, NOISE_STD, rng)
X_val, y_val = generate_clean_set(N_VAL, beta_true, NOISE_STD, rng)
X_test, y_test = generate_clean_set(N_TEST, beta_true, NOISE_STD, rng)

print(f"X_train_clean: {X_train_clean.shape}; y_train_clean: {y_train_clean.shape}")
print(f"X_val: {X_val.shape}; y_val: {y_val.shape}")
print(f"X_test: {X_test.shape}; y_test: {y_test.shape}")
