# Contributors:
# * Contributor: <alexandersafstrom@proton.me>
# * Contributor: <kaisa.arumeel@gmail.com>
# * Contributor: <elindstr@student.chalmers.se>
import sqlite3
import os
import json
from datetime import datetime
import numpy as np
import base64
import io
import tensorflow as tf
import pickle


def serialize_weights(weights):
    # Create a list to store serialized weights
    serialized_layers = []

    for weight_matrix in weights:
        buffer = io.BytesIO()
        # Save each weight matrix separately
        np.save(buffer, weight_matrix, allow_pickle=True)
        # Encode and store each matrix
        serialized_layers.append(base64.b64encode(buffer.getvalue()).decode("utf-8"))

    # Convert list of serialized layers to JSON for storage
    return json.dumps(serialized_layers)


def deserialize_weights(serialized_weights):
    # Parse the JSON string back to list
    serialized_layers = json.loads(serialized_weights)

    # Reconstruct weights layer by layer
    weights = []
    for layer_weights in serialized_layers:
        buffer = io.BytesIO(base64.b64decode(layer_weights.encode("utf-8")))
        weights.append(np.load(buffer, allow_pickle=True))

    return weights


def save_model(
    db_path,
    app_table_name,
    model,
    test_size,
    input_size,
    dropout_rate,
    loss_function,
    num_epochs,
    batch_size,
    learning_rate,
    validation_accuracy,
    tabular_scaler,
    lesion_type_encoder,
    localization_encoder,
    custom_recall,
):
    try:
        # Serialize weights layer by layer
        serialized_weights = serialize_weights(model.get_weights())

        # Serialize and encode the scaler
        pickled_scaler = pickle.dumps(tabular_scaler)
        encoded_scaler = base64.b64encode(pickled_scaler).decode("utf-8")

        # Serialize and encode the lesion_type encoder
        pickled_lesion_encoder = pickle.dumps(lesion_type_encoder)
        encoded_lesion_encoder = base64.b64encode(pickled_lesion_encoder).decode(
            "utf-8"
        )

        # Serialize and encode the localization encoder
        pickled_loc_encoder = pickle.dumps(localization_encoder)
        encoded_loc_encoder = base64.b64encode(pickled_loc_encoder).decode("utf-8")

        # Prepare hyperparameters dict
        hyperparameters = {
            "test_size": float(test_size),  # Ensure numeric values are serializable
            "input_size": input_size,
            "dropout_rate": float(dropout_rate),
            "loss_function": loss_function,
            "num_epochs": int(num_epochs),
            "batch_size": int(batch_size),
            "learning_rate": float(learning_rate),
            "model_architecture": model.to_json(),
            "validation_accuracy": float(validation_accuracy),
            "tabular_scaler": encoded_scaler,
            "lesion_type_encoder": encoded_lesion_encoder,
            "localization_encoder": encoded_loc_encoder,
            "custom_recall": float(custom_recall),
        }

        # Convert hyperparameters to JSON string
        hyperparameters_json = json.dumps(hyperparameters)

        # Get current timestamp
        created_at = int(datetime.now().timestamp())

        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert model data
        cursor.execute(
            f"""
            INSERT INTO {app_table_name} (created_at, weights, hyperparameters)
            VALUES (?, ?, ?)
        """,
            (created_at, serialized_weights, hyperparameters_json),
        )

        # Commit changes and close connection
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error saving model: {str(e)}")
        raise


def load_active_model_from_db(db_path):
    """
    Loads the active model from database with improved weight deserialization
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT models.version, models.weights, models.hyperparameters 
            FROM models
            JOIN model_active activemodels ON models.version = activemodels.model_id
            WHERE activemodels.id = 1
        """
        )

        row = cursor.fetchone()
        if row is None:
            print("No active model found in database")
            return None, None, None

        model_version, serialized_weights, hyperparameters_json = row

        # Parse the hyperparameters
        hyperparameters = json.loads(hyperparameters_json)

        # Ensure model architecture is in the hyperparameters
        if "model_architecture" not in hyperparameters:
            raise ValueError("Model architecture is missing in hyperparameters")

        # Load model architecture from the hyperparameters
        architecture_json = hyperparameters["model_architecture"]

        # Reconstruct the model's structure using the architecture JSON
        model = tf.keras.models.model_from_json(architecture_json)

        # Deserialize the weights from the serialized format
        weights = deserialize_weights(serialized_weights)

        # Set the model's weights
        model.set_weights(weights)

        conn.close()

        return model, hyperparameters, model_version

    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise
