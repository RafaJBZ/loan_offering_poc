import os
from mage_ai.streaming.sinks.base_python import BasePythonSink
from typing import Dict, List
import pandas as pd
import logging

if 'streaming_sink' not in globals():
    from mage_ai.data_preparation.decorators import streaming_sink

@streaming_sink
class CustomSink(BasePythonSink):
    def init_client(self):
        """
        Implement the logic of initializing the client.
        """
        pass

    def batch_write(self, messages: List[Dict]):
        """
        Batch write the messages to the sink.

        For each message, the message format could be one of the following ones:
        1. message is the whole data to be written into the sink
        2. message contains the data and metadata with the format {"data": {...}, "metadata": {...}}
            The data value is the data to be written into the sink. The metadata is used to store
            extra information that can be used in the write method (e.g. timestamp, index, etc.).
        """
        # Define the absolute file path
        file_path = '/mnt/c/Users/rafaj/Documents/loan_offering_poc/offline_server/feature_repo/data/client_features.parquet'
        directory = os.path.dirname(file_path)

        # Create the directory if it does not exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Prepare data for writing
        feature_rows = []
        for msg in messages:
            features = msg.get('features', {})
            feature_row = {
                'client_id': msg.get('client_id'),
                'age': features.get('age'),
                'income': features.get('income'),
                'gender': features.get('gender'),
                'prediction': msg.get('prediction')
            }
            feature_rows.append(feature_row)

        feature_df = pd.DataFrame(feature_rows)

        # Write messages to the file
        try:
            if os.path.exists(file_path):
                existing_df = pd.read_parquet(file_path)
                feature_df = pd.concat([existing_df, feature_df], ignore_index=True)

            feature_df.to_parquet(file_path, index=False)
            logging.info(f"Successfully wrote to {file_path}")
        except Exception as e:
            logging.error(f"Failed to write to {file_path}: {e}")
            raise