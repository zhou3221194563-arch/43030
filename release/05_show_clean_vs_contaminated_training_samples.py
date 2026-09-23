# Cell 5 — Show clean vs contaminated training samples

feature_names = [f"x{i + 1}" for i in range(P)]
sample_table = pd.DataFrame(X_train_observed, columns=feature_names)
sample_table.insert(0, "row_id", np.arange(N_TRAIN))
sample_table["y_clean"] = y_train_clean
sample_table["y_observed"] = y_train_observed
sample_table["response_contaminated"] = response_mask
sample_table["contaminated_feature_count"] = feature_mask.sum(axis=1)

clean_example_ids = np.flatnonzero(~affected_rows)[:5]
contaminated_example_ids = np.flatnonzero(affected_rows)[:5]

print("Clean training examples (observed values equal clean values):")
display(sample_table.iloc[clean_example_ids])

print("Contaminated training examples:")
display(sample_table.iloc[contaminated_example_ids])

if CONTAMINATION_TYPE == "cellwise" and len(contaminated_example_ids):
    first_id = contaminated_example_ids[0]
    changed_names = np.array(feature_names)[feature_mask[first_id]]
    print(f"row {first_id}: contaminated feature cells = {list(changed_names)}")
