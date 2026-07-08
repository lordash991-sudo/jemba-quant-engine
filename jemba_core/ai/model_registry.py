from sklearn.ensemble import RandomForestClassifier


class ModelRegistry:

    MODELS = {

        "random_forest": RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            n_jobs=-1,
        ),

    }

    @classmethod
    def get(cls, name):

        return cls.MODELS[name]
