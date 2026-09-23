# Cell 6 — Train ordinary least-squares linear regression on observed training data
# The intercept is fitted by adding a leading column of ones.

def add_intercept(X):
    return np.column_stack([np.ones(len(X)), X])


X_train_design = add_intercept(X_train_observed)
normal_matrix = X_train_design.T @ X_train_design
normal_target = X_train_design.T @ y_train_observed
theta_hat = np.linalg.solve(normal_matrix, normal_target)

intercept_hat = theta_hat[0]
beta_hat = theta_hat[1:]
y_train_pred = add_intercept(X_train_observed) @ theta_hat
train_mse = np.mean((y_train_observed - y_train_pred) ** 2)

print(f"intercept_hat = {intercept_hat:.3f}")
print(f"training MSE on observed targets = {train_mse:.3f}")
display(
    pd.DataFrame(
        {"beta_true": beta_true, "beta_hat": beta_hat, "difference": beta_hat - beta_true},
        index=feature_names,
    )
)
