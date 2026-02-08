import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn_som.som import SOM
from loguru import logger
import pickle
import os

class DimReducer:
    def __init__(self, n_pca_components: int = 10, som_m: int = 10, som_n: int = 10):
        self.n_pca_components = n_pca_components
        self.pca = None
        self.som = None
        # SOM grid size
        self.som_m = som_m
        self.som_n = som_n
        self.is_fitted = False

    def fit(self, X: pd.DataFrame):
        """
        Fit PCA and SOM on the dataset.
        """
        data = X.values
        if data.shape[1] > self.n_pca_components:
            logger.info(f"Fitting PCA to reduce from {data.shape[1]} to {self.n_pca_components}...")
            self.pca = PCA(n_components=self.n_pca_components)
            data_pca = self.pca.fit_transform(data)
        else:
            self.pca = None
            data_pca = data

        logger.info(f"Fitting SOM ({self.som_m}x{self.som_n})...")
        self.som = SOM(m=self.som_m, n=self.som_n, dim=data_pca.shape[1])
        self.som.fit(data_pca)
        self.is_fitted = True

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Transform data to SOM coordinates.
        Returns array of shape (n_samples, 2) -> [x, y] coordinates on the map.
        """
        if not self.is_fitted:
            raise ValueError("DimReducer not fitted.")
        
        data = X.values
        if self.pca:
            data = self.pca.transform(data)
            
        # SOM prediction returns the cluster index (0 to m*n - 1)
        # We want coordinates to treat as continuous-ish features or just categories
        predictions = self.som.predict(data)
        
        # Convert index to (x, y)
        coords = []
        for p in predictions:
            x = p // self.som_n
            y = p % self.som_n
            coords.append([x, y])
            
        return np.array(coords)

    def save(self, path="models/reducer.pkl"):
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path="models/reducer.pkl"):
        with open(path, 'rb') as f:
            return pickle.load(f)

if __name__ == "__main__":
    # Test
    # Create 15-dim random data
    X = pd.DataFrame(np.random.rand(100, 15))
    reducer = DimReducer()
    reducer.fit(X)
    transformed = reducer.transform(X)
    print(f"Original shape: {X.shape}")
    print(f"Transformed shape: {transformed.shape}")
    print(transformed[:5])
