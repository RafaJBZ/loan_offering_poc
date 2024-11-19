from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer

@transformer
def transform(messages: List[Dict], *args, **kwargs):
    """
    Processes incoming messages from Kafka.

    Args:
        messages (List[Dict]): List of messages from Kafka.

    Returns:
        List[Dict]: Transformed messages ready for export.
    """
    logging.info(f"Transforming {len(messages)} messages.")

    processed_messages = []
    for msg in messages:
        # Extract features and prediction from the message
        features = msg.get('features', {})
        prediction = msg.get('prediction')

        # Create the transformed message
        data = {
            'client_id': msg.get('client_id'),
            'features': {
                'age': features.get('age'),
                'income': features.get('income'),
                'gender': features.get('gender')
            },
            'prediction': prediction
        }
        processed_messages.append(data)

    logging.info(f"Transformed {len(processed_messages)} messages.")
    return processed_messages