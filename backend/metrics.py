# backend/metrics.py
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score

def calculate_metrics(predictions, ground_truth):
    """Model metriklerini hesapla"""
    # Binary threshold uygula
    binary_preds = (predictions > 0.5).astype(np.uint8)
    
    precision = precision_score(ground_truth.flatten(), binary_preds.flatten())
    recall = recall_score(ground_truth.flatten(), binary_preds.flatten()) 
    f1 = f1_score(ground_truth.flatten(), binary_preds.flatten())
    
    return {"precision": precision, "recall": recall, "f1": f1}