
# import numpy as np
# import pickle
# import joblib

# def extract_column_summaries(flat_list, seq_len=50, feat_dim=12):
#     arr = np.array(flat_list, dtype=np.float32).reshape(seq_len, feat_dim)
#     means = arr.mean(axis=0)
#     stds  = arr.std(axis=0)
#     mins  = arr.min(axis=0)
#     maxs  = arr.max(axis=0)
#     meds  = np.median(arr, axis=0)
#     # Flatten per-column stats: [mean, std, min, max, median] × feat_dim
#     summaries = []
#     for i in range(feat_dim):
#         summaries += [means[i], stds[i], mins[i], maxs[i], meds[i]]
#     return summaries

# # svm_wrapper.py (or model.py)

# class SVMWrapper:
#     def __init__(self,
#                  model_path="svm_activity_model.pkl",
#                  scaler_path="scaler.pkl"):
#         # load the SVM
#         with open(model_path, "rb") as f:
#             self.model = joblib.load(f)
#         # load the scaler (only if you saved one)
#         self.scaler = joblib.load(scaler_path)

#     def predict(self, flat_list):
#         # 1) compute your 60-dim summary_feats as before...
#         summary_feats = extract_column_summaries(flat_list, seq_len=50, feat_dim=12)

#         # 2) scale them exactly as in training
#         X = np.array(summary_feats, dtype=np.float32).reshape(1, -1)
#         X_scaled = self.scaler.transform(X)

#         # 3) get probabilities
#         probs = self.model.predict_proba(X_scaled)[0].tolist()
#         return probs





# # xgb_wrapper.py


import numpy as np
import pickle
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)



def extract_column_summaries(flat_list, seq_len=50, feat_dim=12):
    """
    Given a flat list of length seq_len * feat_dim, reshape into (seq_len, feat_dim)
    and compute for each column (feature):
      - mean
      - standard deviation
      - min
      - max
      - median
    Returns a flattened list of column-wise summaries in the order:
      [col0_mean, col0_std, col0_min, col0_max, col0_median,
       col1_mean, col1_std, col1_min, col1_max, col1_median, ...]
    Total length: feat_dim * 5
    """
    arr = np.array(flat_list, dtype=np.float32).reshape(seq_len, feat_dim)
    means = arr.mean(axis=0)
    stds = arr.std(axis=0)
    mins = arr.min(axis=0)
    maxs = arr.max(axis=0)
    meds = np.median(arr, axis=0)
    
    # Interleave per-column summaries
    summaries = []
    for i in range(feat_dim):
        summaries.extend([
            means[i], stds[i], mins[i], maxs[i], meds[i]
        ])
    return summaries

class XGBWrapper:
    def __init__(self, model_path="xgboost_updated.pkl"):
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

    def predict(self, flat_list):
        """
        Returns the soft-probabilities for the single window,
        using column-wise summaries as features.
        """
        # print("RECEIVED:", flat_list)

        # 1. Extract column summaries (12 features -> 12*5 = 60 summary features)
        summary_feats = extract_column_summaries(flat_list, seq_len=50, feat_dim=12)
        
        # print(f"SUMMARY FEATURES (length={len(summary_feats)}):", summary_feats)

        # 2. Prepare input for XGBoost: shape (1, 60)
        X = np.array(summary_feats, dtype=np.float32).reshape(1, -1)

        # 3. Predict probabilities
        proba = self.model.predict_proba(X)[0].tolist()
        # print("PROBS:", proba)
        logging.info(f"PROBS: {proba}")
        return proba
