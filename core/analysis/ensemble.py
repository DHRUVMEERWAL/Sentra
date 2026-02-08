import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed, Input
from loguru import logger
import pickle
import os

class AnomalyEnsemble:
    def __init__(self, contamination=0.01):
        self.contamination = contamination
        self.scaler = StandardScaler()
        
        # Models
        self.iso_forest = IsolationForest(contamination=contamination, random_state=42)
        self.gmm = GaussianMixture(n_components=3, covariance_type='full', random_state=42)
        self.lstm_ae = None # To be built based on input shape
        
        self.is_fitted = False

    def _build_lstm_ae(self, input_shape):
        """Builds a simple LSTM Autoencoder."""
        # input_shape = (timesteps, features)
        timesteps, features = input_shape
        
        inputs = Input(shape=(timesteps, features))
        encoded = LSTM(16, activation='relu', return_sequences=False)(inputs)
        encoded = RepeatVector(timesteps)(encoded)
        decoded = LSTM(16, activation='relu', return_sequences=True)(encoded)
        output = TimeDistributed(Dense(features))(decoded)
        
        model = Model(inputs, output)
        model.compile(optimizer='adam', loss='mse')
        return model

    def fit(self, X: np.ndarray, Sequence_X: np.ndarray = None):
        """
        Fit the ensemble.
        X: 2D array (samples, features) for IF and GMM.
        Sequence_X: 3D array (samples, timesteps, features) for LSTM-AE.
                    If None, LSTM-AE is skipped or needs shaping.
        """
        logger.info("Fitting Scaler...")
        X_scaled = self.scaler.fit_transform(X)
        
        logger.info("Fitting Isolation Forest...")
        self.iso_forest.fit(X_scaled)
        
        logger.info("Fitting GMM...")
        self.gmm.fit(X_scaled)
        
        if Sequence_X is not None:
            logger.info("Fitting LSTM Autoencoder...")
            # Assuming Sequence_X is already sufficient length
            self.lstm_ae = self._build_lstm_ae(Sequence_X.shape[1:])
            self.lstm_ae.fit(Sequence_X, Sequence_X, epochs=10, batch_size=32, verbose=0, shuffle=True)
        else:
            logger.warning("No sequence data provided. LSTM-AE skipped.")
        
        self.is_fitted = True
        logger.info("Ensemble fitted.")

    def score(self, X: np.ndarray, Sequence_X: np.ndarray = None) -> np.ndarray:
        """
        Returns an aggregate anomaly score (0.0 to 1.0 approx).
        Higher = More Anomalous.
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted.")
            
        X_scaled = self.scaler.transform(X)
        n_samples = X.shape[0]
        
        # 1. Isolation Forest Score
        # decision_function: lower is more anomalous (negative).
        # range roughly -1 to 1. We invert it so high is anomalous.
        if_score = -self.iso_forest.decision_function(X_scaled) 
        
        # 2. GMM Score
        # score_samples: log-likelihood. Lower is more anomalous.
        gmm_log_prob = self.gmm.score_samples(X_scaled)
        gmm_score = -gmm_log_prob # Invert
        
        # 3. LSTM-AE Reconstruction Error
        lstm_score = np.zeros(n_samples)
        if self.lstm_ae and Sequence_X is not None:
            reconstruction = self.lstm_ae.predict(Sequence_X)
            mse = np.mean(np.power(Sequence_X - reconstruction, 2), axis=(1, 2))
            lstm_score = mse
        
        # Normalization (Simple MinMax scaling on the fly or just weighted sum)
        # For production, we should track min/max from training.
        # Here we'll just sum them roughly.
        
        # Sigmoid-ish squash to keep in bounds?
        # Let's just return raw sum for now, or a dict.
        
        # Normalize to 0-1 range roughly based on typical values
        # This is a heuristic.
        
        return {
            "isolation_forest": if_score,
            "gmm": gmm_score,
            "lstm_ae": lstm_score,
            "aggregate": (if_score + (gmm_score / 100) + (lstm_score * 10)) # Arbitrary weighting
        }

    def save(self, path="models/ensemble.pkl"):
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Handle Keras model
        lstm_backup = self.lstm_ae
        if self.lstm_ae:
            keras_path = path.replace(".pkl", ".keras")
            self.lstm_ae.save(keras_path)
            self.lstm_ae = None # Detach for pickle
            
        try:
            with open(path, 'wb') as f:
                pickle.dump(self, f)
            logger.info(f"Ensemble saved to {path}")
        finally:
            # Restore to keep object usable
            self.lstm_ae = lstm_backup

    @staticmethod
    def load(path="models/ensemble.pkl"):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at {path}")
            
        with open(path, 'rb') as f:
            ensemble = pickle.load(f)
            
        # Restore Keras model
        keras_path = path.replace(".pkl", ".keras")
        if os.path.exists(keras_path):
            from tensorflow.keras.models import load_model
            ensemble.lstm_ae = load_model(keras_path)
            logger.info(f"Loaded LSTM model from {keras_path}")
            
        return ensemble

if __name__ == "__main__":
    # Test
    model = AnomalyEnsemble()
    X = np.random.rand(100, 10) # 100 samples, 10 features
    
    # Create sequence data: 100 samples, 5 timesteps, 10 features
    Seq_X = np.random.rand(100, 5, 10)
    
    model.fit(X, Seq_X)
    scores = model.score(X, Seq_X)
    print(pd.DataFrame(scores).head())
    
    # Test Save/Load
    model.save("/tmp/test_sentra.pkl")
    loaded = AnomalyEnsemble.load("/tmp/test_sentra.pkl")
    print("Model loaded successfully.")
