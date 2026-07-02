import pandas as pd
from sklearn.cluster import KMeans

# =====================================================
# Load prioritized testcases
# =====================================================

df = pd.read_csv(
    "prioritized_tests.csv"
)

print(
    "Original size:",
    len(df)
)

# =====================================================
# Features for clustering
# =====================================================

X = df[
    [
        "write_en",
        "read_en",
        "fifo_state",
        "data_type",
        "predicted_gain"
    ]
]

# =====================================================
# Number of clusters
# =====================================================

k = 36

k = min(
    k,
    len(df)
)

# =====================================================
# Run clustering
# =====================================================

kmeans = KMeans(
    n_clusters=k,
    random_state=42
)

df["cluster"] = kmeans.fit_predict(
    X
)

# =====================================================
# Pick best testcase from each cluster
# =====================================================

best_tests = df.loc[
    df.groupby("cluster")[
        "predicted_gain"
    ].idxmax()
]

# =====================================================
# Sort again by priority
# =====================================================

best_tests = best_tests.sort_values(
    by="predicted_gain",
    ascending=False
)

# =====================================================
# Save clustered testcases
# =====================================================

best_tests.to_csv(
    "clustered_tests.csv",
    index=False
)

print(
    "Reduced size:",
    len(best_tests)
)

print(
    best_tests.head()
)