import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

df = pd.read_csv("train.csv")

# 🔹 Handle missing values properly

# Numeric columns → fill with 0
num_cols = ["Age", "RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]
df[num_cols] = df[num_cols].fillna(0)

# Categorical columns → fill with 'Unknown'
cat_cols = ["HomePlanet", "CryoSleep", "Cabin", "Destination", "VIP"]
df[cat_cols] = df[cat_cols].fillna("Unknown")

# 🔹 Convert True/False safely
df["CryoSleep"] = df["CryoSleep"].map({True: 1, False: 0, "Unknown": 0})
df["VIP"] = df["VIP"].map({True: 1, False: 0, "Unknown": 0})

# 🔹 Feature engineering
df["TotalSpending"] = (
    df["RoomService"] +
    df["FoodCourt"] +
    df["ShoppingMall"] +
    df["Spa"] +
    df["VRDeck"]
)

# 🔹 Final features
X = df[["Age", "CryoSleep", "VIP", "TotalSpending"]]
y = df["Transported"].astype(int)

# 🔹 Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# 🔹 Save model
pickle.dump(model, open("model.pkl", "wb"))

print("✅ model.pkl created successfully!")