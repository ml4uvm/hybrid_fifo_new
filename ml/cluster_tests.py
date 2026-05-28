import pandas as pd
from sklearn.cluster import KMeans

# Load data
df = pd.read_csv("prioritized_tests.csv")

print("Original size:", len(df))

#  features for clustering
X = df[['opcode', 'a_type', 'b_type', 'predicted_gain']]

# Number of clusters (min 50, dont keep too high it wont reduce)
k = 135

kmeans = KMeans(n_clusters=k, random_state=42)
df['cluster'] = kmeans.fit_predict(X)

# Pick BEST testcase from each cluster
best_tests = df.loc[df.groupby('cluster')['predicted_gain'].idxmax()]

# Sort again
best_tests = best_tests.sort_values(by='predicted_gain', ascending=False)

# Save result
best_tests.to_csv("clustered_tests.csv", index=False)

print("Reduced size:", len(best_tests))
print(best_tests.head())