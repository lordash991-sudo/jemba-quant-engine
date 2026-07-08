class Inference:

    def __init__(self, model):

        self.model = model

    def predict(self, features):

        return self.model.predict(features)
