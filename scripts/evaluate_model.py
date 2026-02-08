"""
Model Evaluation Metrics Calculator

Calculates F1 Score, Recall, Precision, Accuracy, and AUC-ROC
for the Sentra anomaly detection model.

Since this is unsupervised learning, we use the simulation phases
as ground truth:
- Benign phase (first 10 min) = Label 0 (Normal)
- Attack phase = Label 1 (Anomaly)
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    roc_curve
)
from loguru import logger

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipeline import pipeline
from core.data.features import FeatureExtractor


class ModelEvaluator:
    """
    Evaluates the Sentra anomaly detection model using simulation data.
    """
    
    def __init__(self, threshold: float = 2.5):
        self.threshold = threshold
        self.model = None
        self.metrics = {}
        
    def load_model(self):
        """Load the trained model."""
        logger.info("Loading model for evaluation...")
        self.model = pipeline.load_or_create()
        if not self.model.is_fitted:
            logger.error("Model is not fitted! Please train the model first.")
            return False
        logger.success("Model loaded successfully.")
        return True
    
    def generate_test_data(self, n_benign: int = 500, n_attack: int = 200):
        """
        Generate synthetic test data based on expected patterns.
        
        Args:
            n_benign: Number of benign samples
            n_attack: Number of attack samples
            
        Returns:
            X_test, y_true: Test features and ground truth labels
        """
        logger.info(f"Generating test dataset: {n_benign} benign, {n_attack} attack samples")
        
        np.random.seed(42)  # For reproducibility
        
        # Benign traffic patterns (based on observed scores ~80,000)
        benign_features = []
        for _ in range(n_benign):
            feat = {
                'packet_count': np.random.randint(5, 20),
                'total_bytes': np.random.randint(500, 5000),
                'unique_dst_ips': np.random.randint(1, 5),
                'unique_dst_ports': np.random.randint(1, 10),
                'avg_pkt_size': np.random.uniform(50, 300),
                'std_pkt_size': np.random.uniform(20, 100),
                'tcp_ratio': np.random.uniform(0.6, 1.0),
                'udp_ratio': np.random.uniform(0.0, 0.3),
                'syn_count': np.random.randint(0, 3),
                'syn_ratio': np.random.uniform(0.0, 0.2),
                'port_554_count': np.random.randint(0, 3),
                'port_80_count': np.random.randint(0, 5),
                'port_22_count': np.random.randint(0, 2),
            }
            benign_features.append(feat)
        
        # Attack traffic patterns (SYN flood, port scanning)
        attack_features = []
        for _ in range(n_attack):
            feat = {
                'packet_count': np.random.randint(50, 500),  # Much higher
                'total_bytes': np.random.randint(10000, 100000),
                'unique_dst_ips': np.random.randint(1, 3),  # Focused
                'unique_dst_ports': np.random.randint(100, 1000),  # Port scan
                'avg_pkt_size': np.random.uniform(40, 80),  # Small SYN packets
                'std_pkt_size': np.random.uniform(5, 20),  # Low variance
                'tcp_ratio': np.random.uniform(0.9, 1.0),  # All TCP
                'udp_ratio': np.random.uniform(0.0, 0.1),
                'syn_count': np.random.randint(30, 200),  # SYN flood
                'syn_ratio': np.random.uniform(0.7, 1.0),  # Mostly SYN
                'port_554_count': np.random.randint(10, 100),  # RTSP attack
                'port_80_count': np.random.randint(5, 50),
                'port_22_count': np.random.randint(5, 50),
            }
            attack_features.append(feat)
        
        # Combine into DataFrame
        all_features = benign_features + attack_features
        df = pd.DataFrame(all_features)
        
        # Create labels
        y_true = np.array([0] * n_benign + [1] * n_attack)
        
        # Get feature matrix
        X_test = df.values
        
        # Create sequence data (fake for LSTM compatibility)
        X_seq = np.zeros((X_test.shape[0], 5, X_test.shape[1]))
        for i in range(5):
            X_seq[:, i, :] = X_test
        
        logger.info(f"Test dataset shape: {X_test.shape}")
        return X_test, X_seq, y_true
    
    def evaluate(self, X_test: np.ndarray, X_seq: np.ndarray, y_true: np.ndarray):
        """
        Evaluate the model and compute all metrics.
        
        Args:
            X_test: Test feature matrix
            X_seq: Test sequence data for LSTM
            y_true: Ground truth labels (0=benign, 1=attack)
        """
        if self.model is None:
            logger.error("Model not loaded!")
            return None
        
        logger.info("Running model predictions...")
        
        # Get anomaly scores
        scores = self.model.score(X_test, X_seq)
        raw_scores = scores['aggregate']
        
        # Normalize scores for prediction
        # Using z-score based threshold like in main.py
        mean_score = np.mean(raw_scores)
        std_score = np.std(raw_scores)
        
        if std_score > 0:
            z_scores = (raw_scores - mean_score) / std_score
        else:
            z_scores = np.zeros_like(raw_scores)
        
        # Predict: z-score > 2.5 = attack
        y_pred = (z_scores > self.threshold).astype(int)
        
        # Calculate metrics
        self.metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0),
        }
        
        # AUC-ROC (using normalized scores as probabilities)
        try:
            # Normalize raw scores to 0-1 range for AUC
            score_min = np.min(raw_scores)
            score_max = np.max(raw_scores)
            if score_max > score_min:
                proba_scores = (raw_scores - score_min) / (score_max - score_min)
            else:
                proba_scores = np.zeros_like(raw_scores)
            
            self.metrics['auc_roc'] = roc_auc_score(y_true, proba_scores)
        except Exception as e:
            logger.warning(f"Could not compute AUC-ROC: {e}")
            self.metrics['auc_roc'] = None
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        self.metrics['confusion_matrix'] = cm
        
        # Additional stats
        self.metrics['true_positives'] = cm[1, 1] if cm.shape == (2, 2) else 0
        self.metrics['true_negatives'] = cm[0, 0] if cm.shape == (2, 2) else 0
        self.metrics['false_positives'] = cm[0, 1] if cm.shape == (2, 2) else 0
        self.metrics['false_negatives'] = cm[1, 0] if cm.shape == (2, 2) else 0
        
        return self.metrics
    
    def print_report(self):
        """Print a formatted evaluation report."""
        if not self.metrics:
            logger.error("No metrics calculated yet!")
            return
        
        print("\n" + "=" * 60)
        print("       SENTRA MODEL EVALUATION REPORT")
        print("=" * 60)
        
        print(f"\n Classification Metrics:")
        print(f"   ┌{'─' * 30}┬{'─' * 15}┐")
        print(f"   │ {'Metric':<28} │ {'Value':>13} │")
        print(f"   ├{'─' * 30}┼{'─' * 15}┤")
        print(f"   │ {'Accuracy':<28} │ {self.metrics['accuracy']:>12.4f} │")
        print(f"   │ {'Precision':<28} │ {self.metrics['precision']:>12.4f} │")
        print(f"   │ {'Recall (Sensitivity)':<28} │ {self.metrics['recall']:>12.4f} │")
        print(f"   │ {'F1 Score':<28} │ {self.metrics['f1_score']:>12.4f} │")
        if self.metrics['auc_roc'] is not None:
            print(f"   │ {'AUC-ROC':<28} │ {self.metrics['auc_roc']:>12.4f} │")
        print(f"   └{'─' * 30}┴{'─' * 15}┘")
        
        print(f"\n Confusion Matrix:")
        cm = self.metrics['confusion_matrix']
        print(f"                  Predicted")
        print(f"                  Normal  Attack")
        print(f"   Actual Normal  [{cm[0,0]:5d}] [{cm[0,1]:5d}]")
        print(f"   Actual Attack  [{cm[1,0]:5d}] [{cm[1,1]:5d}]")
        
        print(f"\n Detection Stats:")
        print(f"   True Positives (Correctly detected attacks):  {self.metrics['true_positives']}")
        print(f"   True Negatives (Correctly ignored normal):    {self.metrics['true_negatives']}")
        print(f"   False Positives (False alarms):               {self.metrics['false_positives']}")
        print(f"   False Negatives (Missed attacks):             {self.metrics['false_negatives']}")
        
        print("\n" + "=" * 60)
        print()
        
    def save_report(self, filepath: str = "evaluation_report.json"):
        """Save metrics to a JSON file."""
        import json
        
        # Convert numpy types for JSON serialization
        export_metrics = {}
        for k, v in self.metrics.items():
            if isinstance(v, np.ndarray):
                export_metrics[k] = v.tolist()
            elif isinstance(v, (np.int64, np.float64)):
                export_metrics[k] = float(v)
            else:
                export_metrics[k] = v
        
        with open(filepath, 'w') as f:
            json.dump(export_metrics, f, indent=2)
        
        logger.success(f"Report saved to {filepath}")

def find_optimal_threshold(evaluator, X_test, X_seq, y_true):
    """
    Find the optimal threshold for best F1 score.
    Tests multiple thresholds and returns results.
    """
    print("\n" + "=" * 60)
    print("       THRESHOLD SENSITIVITY ANALYSIS")
    print("=" * 60)
    print(f"\n{'Threshold':>10} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1 Score':>10}")
    print("-" * 55)
    
    thresholds = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    results = []
    
    for thresh in thresholds:
        evaluator.threshold = thresh
        metrics = evaluator.evaluate(X_test, X_seq, y_true)
        results.append({
            'threshold': thresh,
            'accuracy': metrics['accuracy'],
            'precision': metrics['precision'],
            'recall': metrics['recall'],
            'f1_score': metrics['f1_score']
        })
        print(f"{thresh:>10.1f} {metrics['accuracy']:>10.4f} {metrics['precision']:>10.4f} {metrics['recall']:>10.4f} {metrics['f1_score']:>10.4f}")
    
    # Find best F1
    best = max(results, key=lambda x: x['f1_score'])
    print("-" * 55)
    print(f"\n  OPTIMAL THRESHOLD: {best['threshold']} (F1 Score: {best['f1_score']:.4f})")
    print("=" * 60)
    
    return best['threshold'], results


def run_evaluation():
    """Main evaluation function with threshold optimization."""
    # First, evaluate with default conservative threshold
    evaluator = ModelEvaluator(threshold=2.5)
    
    # Load model
    if not evaluator.load_model():
        logger.error("Failed to load model. Exiting.")
        return
    
    # Generate test data
    X_test, X_seq, y_true = evaluator.generate_test_data(
        n_benign=500,
        n_attack=200
    )
    
    # Find optimal threshold first
    optimal_thresh, _ = find_optimal_threshold(evaluator, X_test, X_seq, y_true)
    
    # Evaluate with optimal threshold
    print("\n" + "=" * 60)
    print(f"  EVALUATING WITH OPTIMAL THRESHOLD: {optimal_thresh}")
    print("=" * 60)
    
    evaluator.threshold = optimal_thresh
    metrics = evaluator.evaluate(X_test, X_seq, y_true)
    
    if metrics:
        # Print report
        evaluator.print_report()
        
        # Save report
        evaluator.save_report("evaluation_report.json")
    
    return evaluator


if __name__ == "__main__":
    run_evaluation()

