import os
from loguru import logger
from core.analysis.ensemble import AnomalyEnsemble

MODEL_PATH = os.getenv("SENTRA_MODEL_PATH", "models/sentra_v1.pkl")

class ModelPipeline:
    def __init__(self):
        self.model = None
        self.path = MODEL_PATH

    def load_or_create(self):
        """Loads model from disk if exists, else creates new."""
        if os.path.exists(self.path):
            logger.info(f"Loading existing model from {self.path}...")
            try:
                self.model = AnomalyEnsemble.load(self.path)
                logger.success("Model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load model: {e}. Creating new instance.")
                self.model = AnomalyEnsemble()
        else:
            logger.info("No existing model found. Creating new instance.")
            self.model = AnomalyEnsemble()
        
        return self.model

    def save(self):
        """Saves current model to disk."""
        if self.model:
            logger.info(f"Saving model to {self.path}...")
            self.model.save(self.path)
            logger.success("Model saved.")
        else:
            logger.warning("No model to save.")

    def train(self, X, Seq_X):
        """Trains the model."""
        if not self.model:
            self.model = AnomalyEnsemble()
        
        logger.info("Starting training...")
        self.model.fit(X, Seq_X)
        self.save()

pipeline = ModelPipeline()
