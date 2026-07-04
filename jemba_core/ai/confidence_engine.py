class ConfidenceEngine:

    def __init__(self, min_confidence: float = 0.70):
        self.min_confidence = min_confidence

    def evaluate(self, prediction: dict):
        confidence = float(prediction["confidence"])
        buy_probability = float(prediction["buy_probability"])
        sell_probability = float(prediction["sell_probability"])
        raw_prediction = int(prediction["prediction"])

        if confidence < self.min_confidence:
            action = "HOLD"
        else:
            action = "BUY" if raw_prediction == 1 else "SELL"

        if confidence >= 0.90:
            level = "VERY_HIGH"
        elif confidence >= 0.80:
            level = "HIGH"
        elif confidence >= 0.70:
            level = "GOOD"
        else:
            level = "LOW"

        return {
            "action": action,
            "confidence": round(confidence, 4),
            "confidence_percent": round(confidence * 100, 2),
            "buy_probability": round(buy_probability, 4),
            "sell_probability": round(sell_probability, 4),
            "level": level,
        }
