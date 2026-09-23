# Cell 7 — Evaluate on clean validation/test data

def regression_metrics(X, y, theta, beta_reference):
    predictions = add_intercept(X) @ theta
    residuals = y - predictions
    mse = np.mean(residuals**2)
    mae = np.mean(np.abs(residuals))
    r2 = 1.0 - np.sum(residuals**2) / np.sum((y - y.mean()) ** 2)
    parameter_error = np.linalg.norm(theta[1:] - beta_reference)
    relative_parameter_error = parameter_error / np.linalg.norm(beta_reference)
    return {
        "MSE": mse,
        "MAE": mae,
        "R2": r2,
        "parameter_L2_error": parameter_error,
        "relative_parameter_error": relative_parameter_error,
    }


validation_metrics = regression_metrics(X_val, y_val, theta_hat, beta_true)
test_metrics = regression_metrics(X_test, y_test, theta_hat, beta_true)
evaluation_table = pd.DataFrame([validation_metrics, test_metrics], index=["clean validation", "clean test"])
display(evaluation_table)
