import pandas as pd

from jemba_core.ai.feature_engineering import FeatureEngineering
from jemba_core.ai.label_generator import LabelGenerator


class DatasetBuilder:
    def __init__(self):
        self.features = FeatureEngineering()
        self.labels = LabelGenerator()

    def build(self, csv_path: str) -> pd.DataFrame:
        df = pd.read_csv(csv_path)
        featured = self.features.transform(df)
        return self.labels.generate(featured)
