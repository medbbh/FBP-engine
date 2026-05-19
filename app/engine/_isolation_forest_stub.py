# v2 enhancement: replace statistical thresholds with ensemble anomaly detection.
# Requires: scikit-learn>=1.4
# To enable: install scikit-learn, uncomment, and wire into detect_anomalies as a second pass.
#
# from sklearn.ensemble import IsolationForest
# import numpy as np
#
# class IsolationForestDetector:
#     def __init__(self, contamination: float = 0.05):
#         self._model = IsolationForest(contamination=contamination, random_state=42)
#         self._fitted = False
#
#     def fit(self, feature_matrix: np.ndarray) -> None:
#         self._model.fit(feature_matrix)
#         self._fitted = True
#
#     def predict(self, features: np.ndarray) -> bool:
#         """Returns True if the sample is flagged as an anomaly."""
#         if not self._fitted:
#             raise RuntimeError("Call fit() before predict()")
#         return self._model.predict(features.reshape(1, -1))[0] == -1
#
#     def score(self, features: np.ndarray) -> float:
#         """Returns the anomaly score (lower = more anomalous)."""
#         if not self._fitted:
#             raise RuntimeError("Call fit() before predict()")
#         return float(self._model.score_samples(features.reshape(1, -1))[0])
