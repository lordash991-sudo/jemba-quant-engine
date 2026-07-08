from .models import WalkForwardWindow


class WalkForwardSplitter:
    def __init__(
        self,
        train_size: int,
        test_size: int,
        step: int,
    ):
        self.train_size = train_size
        self.test_size = test_size
        self.step = step

    def split(self, total_rows: int):
        windows = []

        start = 0

        while start + self.train_size + self.test_size <= total_rows:
            windows.append(
                WalkForwardWindow(
                    train_start=start,
                    train_end=start + self.train_size,
                    test_start=start + self.train_size,
                    test_end=start + self.train_size + self.test_size,
                )
            )

            start += self.step

        return windows
