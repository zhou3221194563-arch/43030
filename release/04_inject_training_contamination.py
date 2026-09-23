# Cell 4 — Inject contamination into training set only
# X_train_clean and y_train_clean are never modified in place.

def inject_contamination(X_clean, y_clean, contamination_type, ratio, magnitude, noise_std, generator):
    """Return observed training data and masks describing every changed value.

    response: a ratio of training rows receives +/- magnitude * noise_std in y.
    cellwise: a ratio of feature cells receives +/- magnitude in X; the target
    remains generated from the original clean features.
    """
    X_observed = X_clean.copy()
    y_observed = y_clean.copy()
    response_mask = np.zeros(len(y_clean), dtype=bool)
    feature_mask = np.zeros_like(X_clean, dtype=bool)

    if contamination_type == "response":
        response_mask = generator.random(len(y_clean)) < ratio
        signs = generator.choice([-1.0, 1.0], size=response_mask.sum())
        y_observed[response_mask] += signs * magnitude * noise_std
    elif contamination_type == "cellwise":
        feature_mask = generator.random(X_clean.shape) < ratio
        signs = generator.choice([-1.0, 1.0], size=feature_mask.sum())
        X_observed[feature_mask] += signs * magnitude
    else:
        raise ValueError("contamination_type must be 'response' or 'cellwise'.")

    return X_observed, y_observed, response_mask, feature_mask


X_train_observed, y_train_observed, response_mask, feature_mask = inject_contamination(
    X_train_clean,
    y_train_clean,
    CONTAMINATION_TYPE,
    CONTAMINATION_RATIO,
    CONTAMINATION_MAGNITUDE,
    NOISE_STD,
    rng,
)

affected_rows = response_mask | feature_mask.any(axis=1)
print(f"contamination type: {CONTAMINATION_TYPE}")
print(f"affected training rows: {affected_rows.sum()} / {N_TRAIN}")
print(f"contaminated feature cells: {feature_mask.sum()} / {N_TRAIN * P}")
print("Validation and test data remain clean.")
