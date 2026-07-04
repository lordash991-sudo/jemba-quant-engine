class RankingEngine:

    def rank(self, predictions):

        ranked = sorted(
            predictions,
            key=lambda x: x["confidence"],
            reverse=True
        )

        return ranked

    def best(self, predictions):

        ranked = self.rank(predictions)

        if len(ranked) == 0:
            return None

        return ranked[0]
