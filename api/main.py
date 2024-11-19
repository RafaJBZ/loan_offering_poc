from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.pyfunc
import pandas as pd
from feature_transformations import compute_features
from kafka import KafkaProducer
import json
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Load the model from MLflow
mlflow.set_tracking_uri("http://localhost:5000")
model_name = "LoanDefaultModel"
model_version = "4"
model = mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}/{model_version}")

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)


# Pydantic model for request body
class ClientData(BaseModel):
    client_id: int
    age: int
    income: float
    gender: str  # 'M' or 'F'


@app.post("/predict")
def predict(data: ClientData):
    logging.info(f"Received data: {data}")
    # Convert request data to DataFrame
    raw_data = pd.DataFrame([data.dict()])

    # Compute features
    features = compute_features(raw_data)

    # Handle missing or invalid features
    if features.isnull().values.any():
        raise HTTPException(status_code=400, detail="Invalid input data")

    # Make prediction
    prediction = model.predict(features)
    default_probability = prediction[0]

    # Publish raw data and features to Kafka
    message = {
        'client_id': data.client_id,
        'raw_data': data.dict(),
        'features': features.to_dict(orient='records')[0],
        'prediction': float(default_probability)
    }
    producer.send('loan_predictions', value=message)

    return {"default_probability": float(default_probability)}