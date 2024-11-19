import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import mlflow
import mlflow.sklearn
from feature_transformations import compute_features

# Load historical raw data
raw_data = pd.DataFrame({
    'client_id': [1, 2, 3, 4],
    'age': [25, 40, 35, 50],
    'income': [50000, 80000, 60000, 70000],
    'gender': ['M', 'F', 'M', 'F'],
    'default': [0, 1, 0, 1],  # Simulated labels with at least two classes
})

# Compute features
features = compute_features(raw_data)

# Prepare training data
X = features
y = raw_data['default']

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = LogisticRegression()
model.fit(X_train, y_train)

# Evaluate model
accuracy = model.score(X_test, y_test)

# Log model with MLflow
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("Loan Default Prediction")

with mlflow.start_run():
    mlflow.log_metric("accuracy", accuracy)
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        registered_model_name="LoanDefaultModel",
    )