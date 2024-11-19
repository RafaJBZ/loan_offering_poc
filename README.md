# Loan Offering POC

## Overview

This Proof of Concept (POC) demonstrates a real-time loan offering automation system using **Mage.ai**, **Feast Feature Store**, and **Apache Kafka**. The system ingests loan application data from Kafka, processes it through a Mage.ai pipeline, and stores the transformed features in Feast for model training and inference.

## Prerequisites

Ensure you have the following installed on your system:

- **Python 3.8+**
- **Docker & Docker Compose**
- **Git**

## Installation

1. **Clone the Repository**

   ```bash
   git clone git@github.com:RafaJBZ/loan_offering_poc.git
   cd loan_offering_poc
   ```

2. **Set Up Python Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Start Services with Docker Compose**

   This will launch Kafka and any other required services.

   ```bash
   docker-compose up -d
   ```

## Configuration

### Kafka Setup

1. **Create Kafka Topic**

   ```bash
   docker exec -it loan_offering_poc_kafka_1 bash
   kafka-topics.sh --create --topic loan_predictions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   exit
   ```

2. **Produce Sample Messages**

   ```bash
   docker exec -it loan_offering_poc_kafka_1 bash
   kafka-console-producer.sh --topic loan_predictions --bootstrap-server localhost:9092
   ```

   Enter sample JSON messages, e.g.,

   ```json
   {"client_id": 1, "age": 30, "income": 55000, "gender": 1}
   {"client_id": 2, "age": 45, "income": 72000, "gender": 0}
   ```

### Feast Setup

1. **Navigate to Offline Server Directory**

   ```bash
   cd offline_server/feature_repo
   ```

2. **Configure feature_store.yaml**

   Ensure the `feature_store.yaml` points to the correct data directory.

   ```yaml
   project: loan_default_project
   registry: data/registry.db
   provider: local

   entity_key_serialization_version: 2

   offline_store:
     type: file
     file_options:
       path: ../data
   ```

3. **Apply Feast Configuration**

   ```bash
   feast apply
   ```

### Mage.ai Pipeline Setup

1. **Navigate to Processor Pipeline Directory**

   ```bash
   cd ../processor_pipeline
   ```

2. **Start the Mage.ai Pipeline**

   ```bash
   mage run feature_storage
   ```

## Running the API

1. **Navigate to API Directory**

   ```bash
   cd ../api
   ```

2. **Start the API Server**

   ```bash
   uvicorn api.main:app --reload
   ```

   The API should be accessible at [http://localhost:8000](http://localhost:8000) (or the configured port).

## Testing

1. **Send Test Data to Kafka**

   Use the Kafka console producer to send sample loan application data as shown in the Kafka Setup section.

2. **Verify Data Processing**

   ```python
   from feast import FeatureStore
   import pandas as pd

   store = FeatureStore(repo_path='offline_server/feature_repo')

   entity_df = pd.DataFrame({
       'client_id': [1, 2],
       'event_timestamp': pd.to_datetime(['2021-01-01', '2021-01-02'])
   })

   features = [
       'client_features:age',
       'client_features:income',
       'client_features:gender',
   ]

   training_df = store.get_historical_features(
       entity_df=entity_df,
       features=features
   ).to_df()

   print(training_df)
   ```

## Troubleshooting

- **Pipeline Errors**:
  - Ensure all decorators and function signatures in Mage.ai pipeline blocks are correct.
  - Verify file paths and directory permissions.
  - Check Docker services are running properly.

- **Feast Issues**:
  - Confirm `feature_store.yaml` is correctly configured.
  - Ensure `feast apply` runs without errors.

- **Kafka Problems**:
  - Verify Kafka is running and the topic exists.
  - Check network configurations and firewall settings.

## License

This project is licensed under the MIT License.
