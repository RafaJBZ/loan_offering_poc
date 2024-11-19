import pandas as pd

def compute_features(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Compute features from raw data.
    """
    features = pd.DataFrame()
    features['age'] = raw_data['age']
    features['income'] = raw_data['income']
    # Convert 'gender' to numeric encoding
    features['gender'] = raw_data['gender'].map({'M': 0, 'F': 1})
    # Fill missing values
    features.fillna(0, inplace=True)
    return features
