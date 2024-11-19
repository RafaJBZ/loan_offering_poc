from datetime import timedelta
import pandas as pd

from feast import (
    Entity,
    FeatureService,
    FeatureView,
    Field,
    FileSource,
    Project,
    PushSource,
    RequestSource,
)
from feast.feature_logging import LoggingConfig
from feast.infra.offline_stores.file_source import FileLoggingDestination
from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float64, Int64

# Define the project
project = Project(name="offline_server", description="A project for client features")

# Define the data source
client_features_source = FileSource(
    name="client_features_source",
    path="data/client_features.parquet",
    timestamp_field="event_timestamp",
)

# Define the client entity
client = Entity(
    name="client_id",
    join_keys=["client_id"],
    description="Client identifier",
)

# Define feature view
client_features_view = FeatureView(
    name="client_features",
    entities=[client],
    ttl=timedelta(days=365),
    schema=[
        Field(name="age", dtype=Int64),
        Field(name="income", dtype=Float64),
        Field(name="gender", dtype=Int64),
    ],
    online=True,
    source=client_features_source,
    tags={"team": "credit_team"},
)

# Define input request source
input_request = RequestSource(
    name="vals_to_add",
    schema=[
        Field(name="val_to_add", dtype=Int64),
        Field(name="val_to_add_2", dtype=Int64),
    ],
)

# Define on-demand feature view
@on_demand_feature_view(
    sources=[client_features_view, input_request],
    schema=[
        Field(name="income_plus_val1", dtype=Float64),
        Field(name="income_plus_val2", dtype=Float64),
    ],
)
def transformed_income(inputs: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df["income_plus_val1"] = inputs["income"] + inputs["val_to_add"]
    df["income_plus_val2"] = inputs["income"] + inputs["val_to_add_2"]
    return df

# Define feature service
client_features_service = FeatureService(
    name="credit_scoring_features",
    features=[
        client_features_view,
        transformed_income,
    ],
    logging_config=LoggingConfig(
        destination=FileLoggingDestination(path="data")
    ),
)