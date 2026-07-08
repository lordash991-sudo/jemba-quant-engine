from sklearn.ensemble import (
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)


class EnsembleFactory:
    @staticmethod
    def build():

        return VotingClassifier(
            estimators=[
                (
                    "rf",
                    RandomForestClassifier(
                        n_estimators=300,
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
                (
                    "et",
                    ExtraTreesClassifier(
                        n_estimators=300,
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
                (
                    "gb",
                    GradientBoostingClassifier(
                        random_state=42,
                    ),
                ),
            ],
            voting="soft",
        )
