class PO3Engine:
    def detect(self, df):
        if "ATR" not in df.columns:
            raise ValueError(
                "El DataFrame debe tener columna ATR. "
                "Usa FeatureEngine.generate(df) primero."
            )

        trades = []
        return trades
