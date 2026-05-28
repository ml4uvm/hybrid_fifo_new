import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import joblib

# STEP 1: Load dataset
df = pd.read_csv("../results/coverage_log.csv")

print("Dataset loaded:")
print(df.head())

# STEP 2: columns
df = df[['opcode', 'a_type', 'b_type', 'gain_label']]

# STEP 3: encoding 
type_map = {
    "ZERO": 0,
    "SMALL": 1,
    "LARGE": 2,
    "NEG": 3
}

df['a_type'] = df['a_type'].map(type_map)
df['b_type'] = df['b_type'].map(type_map)

# STEP 4: make them numeric types
df['opcode'] = df['opcode'].astype(int)
df['gain_label'] = df['gain_label'].astype(int)

# STEP 5: Define features and target
X = df[['opcode', 'a_type', 'b_type']]
y = df['gain_label']

# STEP 6: Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

print("Model trained!")

# STEP 7: Predict probability of coverage gain
df['predicted_gain'] = model.predict_proba(X)[:, 1]

# STEP 8: Sort testcases
df_sorted = df.sort_values(by='predicted_gain', ascending=False)

print("Top prioritized testcases:")
print(df_sorted.head())

# STEP 9: Save prioritized list
df_sorted.to_csv("prioritized_tests.csv", index=False)
print("Saved prioritized_tests.csv")

# STEP 10: Save model
joblib.dump(model, "model.pkl")
print("Model saved as model.pkl")

# STEP 11: Plot graph
plt.plot(df_sorted['predicted_gain'].values)
plt.title("Testcase Priority Curve")
plt.xlabel("Testcases")
plt.ylabel("Predicted Coverage Gain")
plt.savefig("priority_plot.png")
print("Plot saved as priority_plot.png")