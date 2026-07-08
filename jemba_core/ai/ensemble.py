from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import VotingClassifier


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
