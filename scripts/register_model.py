import mlflow
from mlflow.tracking import MlflowClient
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Set the tracking URI if it's not the default
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_URI)

client = MlflowClient()

# Get run_id from environment variable or file
run_id = os.getenv("RUN_ID")
if not run_id:
    # Si no está en env var, leer del archivo
    with open("run_id.txt", "r") as f:
        run_id = f.read().strip()

model_name = os.getenv("MODEL_NAME", "no_name")

# Register the model using the run_id
model_uri = f"runs:/{run_id}/model"

print(f"Registering model '{model_name}' from run: {run_id}")

# Register the model
result = mlflow.register_model(
    model_uri=model_uri,
    name=model_name
)

print(f"Model registered with version: {result.version}")

# Transition to Staging
client.transition_model_version_stage(
    name=model_name,
    version=result.version,
    stage="Staging"
)

print(f"Model version {result.version} transitioned to Staging")

# Set alias
client.set_registered_model_alias(model_name, "champion", result.version)

print(f"Model alias 'champion' set to version {result.version}")