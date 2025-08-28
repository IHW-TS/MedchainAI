from typing import Dict, List, Tuple
import numpy as np

FEATURES = [
    "age",
    "bmi",
    "resting_hr",
    "systolic_bp",
    "weekly_minutes_exercise",
    "smoker",
    "family_history",
    "sex"
]

NUM_FEATURES = ["age", "bmi", "resting_hr", "systolic_bp", "weekly_minutes_exercise"]
BIN_FEATURES = ["smoker", "family_history", "sex"]

MEAN = {
    "age": 45.0,
    "bmi": 26.0,
    "resting_hr": 68.0,
    "systolic_bp": 125.0,
    "weekly_minutes_exercise": 180.0
}
STD = {
    "age": 12.0,
    "bmi": 5.0,
    "resting_hr": 10.0,
    "systolic_bp": 15.0,
    "weekly_minutes_exercise": 120.0
}

COEF = {
    "age": 0.25,
    "bmi": 0.5,
    "resting_hr": 0.2,
    "systolic_bp": 0.15,
    "weekly_minutes_exercise": -0.12,
    "smoker": 0.7,
    "family_history": 0.5,
    "sex": 0.2
}
INTERCEPT = 0.0

def _sigmoid(z: float) -> float:
    return 1.0 / (1.0 + np.exp(-z))

def standardize_numeric(row: Dict[str, float]) -> Dict[str, float]:
    z = {}
    for k in NUM_FEATURES:
        z[k] = (float(row[k]) - MEAN[k]) / (STD[k] if STD[k] != 0 else 1.0)
    return z

def predict_proba(row: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    znum = standardize_numeric(row)
    z = INTERCEPT
    contrib = {}
    for k in NUM_FEATURES:
        c = COEF[k] * znum[k]
        contrib[k] = c
        z += c
    for k in BIN_FEATURES:
        v = float(row[k])
        c = COEF[k] * v
        contrib[k] = c
        z += c
    proba = _sigmoid(z)
    return proba, contrib

def global_importance() -> List[Tuple[str, float]]:
    out = [(k, abs(COEF[k])) for k in FEATURES]
    out.sort(key=lambda t: t[1], reverse=True)
    return out
