from __future__ import annotations


class ModelRegistry:
    def __init__(self):
        self._models = {}

    def register(self, name: str, model):

        self._models[name] = model

    def get(self, name: str):

        if name not in self._models:
            raise KeyError(name)

        return self._models[name]
