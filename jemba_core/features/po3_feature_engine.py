from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PO3FeatureConfig:
    """
    Configuración del motor cuantitativo PO3.

    Los valores base reflejan la lógica principal del indicador
    ICT Power of Three utilizado como referencia:

    - ATR de 50 periodos.
    - Acumulación larga de 40 barras.
    - Expansión del rango de acumulación de 0.5 ATR.
    - Manipulación mínima de 0.6 ATR.
    """

    atr_length: int = 50
    accumulation_length: int = 40
    accumulation_atr_multiplier: float = 5.0
    accumulation_expand_multiplier: float = 0.5
    manipulation_atr_multiplier: float = 0.6

    ema_fast: int = 20
    ema_medium: int = 50
    ema_slow: int = 100
    ema_macro: int = 200

    rsi_length: int = 14
    roc_length: int = 10
    volume_length: int = 20
    structure_length: int = 20

    breakout_method: str = "wick"

    def __post_init__(self) -> None:
        if self.atr_length < 2:
            raise ValueError("ATR_LENGTH_MUST_BE_AT_LEAST_2")

        if self.accumulation_length < 2:
            raise ValueError(
                "ACCUMULATION_LENGTH_MUST_BE_AT_LEAST_2"
            )

        if self.accumulation_atr_multiplier <= 0:
            raise ValueError(
                "ACCUMULATION_ATR_MULTIPLIER_MUST_BE_POSITIVE"
            )

        if self.accumulation_expand_multiplier < 0:
            raise ValueError(
                "ACCUMULATION_EXPAND_MULTIPLIER_MUST_BE_NON_NEGATIVE"
            )

        if self.manipulation_atr_multiplier <= 0:
            raise ValueError(
                "MANIPULATION_ATR_MULTIPLIER_MUST_BE_POSITIVE"
            )

        method = self.breakout_method.strip().lower()

        if method not in {"wick", "close"}:
            raise ValueError(
                "BREAKOUT_METHOD_MUST_BE_WICK_OR_CLOSE"
            )


class PO3FeatureEngine:
    """
    Generador de variables para un modelo de clasificación PO3.

    Este motor NO abre operaciones y NO genera órdenes.

    Su responsabilidad es convertir velas OHLCV en variables
    cuantitativas que describen:

    1. Tendencia.
    2. Volatilidad.
    3. Momentum.
    4. Volumen.
    5. Estructura.
    6. Acumulación.
    7. Manipulación.
    8. Distribución.
    9. Contexto temporal.
    """

    REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
        "open",
        "high",
        "low",
        "close",
        "volume",
    )

    OUTPUT_FEATURES: Final[tuple[str, ...]] = (
        # Precio base
        "OPEN",
        "HIGH",
        "LOW",
        "CLOSE",
        "VOLUME",

        # Tendencia
        "EMA20",
        "EMA50",
        "EMA100",
        "EMA200",
        "EMA20_GT_EMA50",
        "EMA50_GT_EMA100",
        "EMA100_GT_EMA200",
        "EMA50_GT_EMA200",
        "DIST_EMA20",
        "DIST_EMA50",
        "DIST_EMA100",
        "DIST_EMA200",
        "EMA20_SLOPE",
        "EMA50_SLOPE",
        "EMA200_SLOPE",
        "TREND_SCORE",

        # Momentum
        "RSI",
        "ROC",
        "RETURN_1",
        "RETURN_3",
        "RETURN_6",
        "MOMENTUM_10",

        # Volatilidad y vela
        "TR",
        "ATR",
        "ATR_PCT",
        "ATR_RATIO",
        "BODY",
        "BODY_PCT",
        "RANGE",
        "RANGE_PCT",
        "UPPER_WICK",
        "LOWER_WICK",
        "UPPER_WICK_PCT",
        "LOWER_WICK_PCT",
        "BULLISH",
        "BEARISH",
        "DOJI",

        # Volumen
        "VOL_SMA20",
        "VOL_RATIO",
        "VOL_ZSCORE",
        "PRICE_VOLUME_IMPULSE",

        # Estructura
        "HIGH20",
        "LOW20",
        "DIST_HIGH20",
        "DIST_LOW20",
        "BREAK_HIGH20",
        "BREAK_LOW20",
        "RANGE_POSITION",

        # Acumulación PO3
        "ACC_HIGH",
        "ACC_LOW",
        "ACC_RANGE",
        "ACC_RANGE_PCT",
        "ACC_ATR_RATIO",
        "ACC_EXPANDED_HIGH",
        "ACC_EXPANDED_LOW",
        "DIST_ACC_HIGH",
        "DIST_ACC_LOW",
        "INSIDE_ACC",
        "ACCUMULATION_VALID",
        "ACCUMULATION_BARS",

        # Manipulación PO3
        "MANIPULATION_UP",
        "MANIPULATION_DOWN",
        "MANIPULATION_DIRECTION",
        "MANIPULATION_DISTANCE",
        "MANIPULATION_ATR",
        "LIQUIDITY_SWEEP_HIGH",
        "LIQUIDITY_SWEEP_LOW",

        # Distribución y señal
        "PO3_STATE",
        "PO3_LONG_SETUP",
        "PO3_SHORT_SETUP",
        "PO3_SIGNAL",
        "BREAKOUT_FORCE",
        "DISTRIBUTION_BODY_ATR",
        "DISTRIBUTION_RANGE_ATR",

        # Contexto temporal
        "HOUR",
        "DAY_OF_WEEK",
        "ASIA_SESSION",
        "LONDON_SESSION",
        "NEW_YORK_SESSION",
    )

    def __init__(
        self,
        config: PO3FeatureConfig | None = None,
    ) -> None:
        self.config = config or PO3FeatureConfig()

    def build(
        self,
        market: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Genera todas las variables PO3 sin utilizar información futura.

        Parameters
        ----------
        market:
            DataFrame con open, high, low, close y volume.
            Puede incluir timestamp, date o datetime.

        Returns
        -------
        pandas.DataFrame
            Datos originales normalizados más las variables PO3.
        """

        frame = self._prepare_market(market)

        frame = self._add_trend_features(frame)
        frame = self._add_momentum_features(frame)
        frame = self._add_volatility_features(frame)
        frame = self._add_volume_features(frame)
        frame = self._add_structure_features(frame)
        frame = self._add_po3_features(frame)
        frame = self._add_time_features(frame)

        frame.replace(
            [np.inf, -np.inf],
            np.nan,
            inplace=True,
        )

        return frame

    def feature_matrix(
        self,
        market: pd.DataFrame,
        *,
        dropna: bool = True,
    ) -> pd.DataFrame:
        """
        Devuelve únicamente las columnas aptas para el modelo.
        """

        frame = self.build(market)

        matrix = frame.loc[
            :,
            list(self.OUTPUT_FEATURES),
        ].copy()

        # Estas columnas representan eventos discretos de PO3.
        #
        # Cuando no existe manipulaci?n o distribuci?n en una vela,
        # su valor correcto es cero, no NaN. Mantener NaN aqu? hac?a
        # que dropna() eliminara todas las filas del dataset.
        sparse_event_features = (
            "MANIPULATION_DISTANCE",
            "MANIPULATION_ATR",
            "BREAKOUT_FORCE",
            "DISTRIBUTION_BODY_ATR",
            "DISTRIBUTION_RANGE_ATR",
        )

        matrix.loc[
            :,
            list(sparse_event_features),
        ] = (
            matrix.loc[
                :,
                list(sparse_event_features),
            ]
            .fillna(0.0)
        )

        if dropna:
            matrix = (
                matrix
                .dropna()
                .reset_index(drop=True)
            )

        return matrix

    def latest(
        self,
        market: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Devuelve la última fila válida para inferencia.
        """

        matrix = self.feature_matrix(
            market,
            dropna=True,
        )

        if matrix.empty:
            raise ValueError(
                "NO_VALID_PO3_FEATURE_ROWS"
            )

        return matrix.tail(1).copy()

    def _prepare_market(
        self,
        market: pd.DataFrame,
    ) -> pd.DataFrame:
        if not isinstance(market, pd.DataFrame):
            raise TypeError(
                "MARKET_MUST_BE_A_PANDAS_DATAFRAME"
            )

        if market.empty:
            raise ValueError("MARKET_DATA_IS_EMPTY")

        frame = market.copy()

        frame.columns = [
            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            for column in frame.columns
        ]

        aliases = {
            "timestamp": (
                "timestamp",
                "datetime",
                "date",
                "time",
                "open_time",
                "opentime",
            ),
            "open": (
                "open",
                "open_price",
                "openprice",
                "o",
            ),
            "high": (
                "high",
                "high_price",
                "highprice",
                "h",
            ),
            "low": (
                "low",
                "low_price",
                "lowprice",
                "l",
            ),
            "close": (
                "close",
                "close_price",
                "closeprice",
                "c",
            ),
            "volume": (
                "volume",
                "vol",
                "base_volume",
                "basevolume",
                "v",
            ),
        }

        rename_map: dict[str, str] = {}

        for canonical, options in aliases.items():
            if canonical in frame.columns:
                continue

            for option in options:
                if option in frame.columns:
                    rename_map[option] = canonical
                    break

        frame.rename(
            columns=rename_map,
            inplace=True,
        )

        missing = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in frame.columns
        ]

        if missing:
            raise ValueError(
                f"MISSING_OHLCV_COLUMNS: {missing}"
            )

        for column in self.REQUIRED_COLUMNS:
            frame[column] = pd.to_numeric(
                frame[column],
                errors="coerce",
            )

        frame.dropna(
            subset=list(self.REQUIRED_COLUMNS),
            inplace=True,
        )

        frame = frame[
            (frame["open"] > 0)
            & (frame["high"] > 0)
            & (frame["low"] > 0)
            & (frame["close"] > 0)
            & (frame["volume"] >= 0)
        ].copy()

        frame = frame[
            (frame["high"] >= frame["low"])
            & (frame["high"] >= frame["open"])
            & (frame["high"] >= frame["close"])
            & (frame["low"] <= frame["open"])
            & (frame["low"] <= frame["close"])
        ].copy()

        if frame.empty:
            raise ValueError(
                "NO_VALID_OHLCV_ROWS"
            )

        if "timestamp" in frame.columns:
            frame["timestamp"] = self._parse_timestamp(
                frame["timestamp"]
            )

            frame.sort_values(
                "timestamp",
                inplace=True,
            )

            frame.drop_duplicates(
                subset=["timestamp"],
                keep="last",
                inplace=True,
            )

        frame.reset_index(
            drop=True,
            inplace=True,
        )

        return frame

    @staticmethod
    def _parse_timestamp(
        values: pd.Series,
    ) -> pd.Series:
        if pd.api.types.is_numeric_dtype(values):
            numeric = pd.to_numeric(
                values,
                errors="coerce",
            )

            median = numeric.dropna().median()

            if pd.isna(median):
                return pd.to_datetime(
                    numeric,
                    errors="coerce",
                    utc=True,
                )

            unit = (
                "ms"
                if median > 10_000_000_000
                else "s"
            )

            return pd.to_datetime(
                numeric,
                unit=unit,
                errors="coerce",
                utc=True,
            )

        return pd.to_datetime(
            values,
            errors="coerce",
            utc=True,
        )

    def _add_trend_features(
        self,
        frame: pd.DataFrame,
    ) -> pd.DataFrame:
        config = self.config
        close = frame["close"]

        frame["OPEN"] = frame["open"]
        frame["HIGH"] = frame["high"]
        frame["LOW"] = frame["low"]
        frame["CLOSE"] = frame["close"]
        frame["VOLUME"] = frame["volume"]

        frame["EMA20"] = close.ewm(
            span=config.ema_fast,
            adjust=False,
        ).mean()

        frame["EMA50"] = close.ewm(
            span=config.ema_medium,
            adjust=False,
        ).mean()

        frame["EMA100"] = close.ewm(
            span=config.ema_slow,
            adjust=False,
        ).mean()

        frame["EMA200"] = close.ewm(
            span=config.ema_macro,
            adjust=False,
        ).mean()

        frame["EMA20_GT_EMA50"] = (
            frame["EMA20"] > frame["EMA50"]
        ).astype(int)

        frame["EMA50_GT_EMA100"] = (
            frame["EMA50"] > frame["EMA100"]
        ).astype(int)

        frame["EMA100_GT_EMA200"] = (
            frame["EMA100"] > frame["EMA200"]
        ).astype(int)

        frame["EMA50_GT_EMA200"] = (
            frame["EMA50"] > frame["EMA200"]
        ).astype(int)

        for period in (20, 50, 100, 200):
            ema_column = f"EMA{period}"
            distance_column = f"DIST_EMA{period}"

            frame[distance_column] = (
                frame["close"] - frame[ema_column]
            ) / frame[ema_column]

        frame["EMA20_SLOPE"] = (
            frame["EMA20"].pct_change(3)
        )

        frame["EMA50_SLOPE"] = (
            frame["EMA50"].pct_change(5)
        )

        frame["EMA200_SLOPE"] = (
            frame["EMA200"].pct_change(10)
        )

        frame["TREND_SCORE"] = (
            frame["EMA20_GT_EMA50"]
            + frame["EMA50_GT_EMA100"]
            + frame["EMA100_GT_EMA200"]
            + (frame["close"] > frame["EMA200"]).astype(int)
        ) / 4.0

        return frame

    def _add_momentum_features(
        self,
        frame: pd.DataFrame,
    ) -> pd.DataFrame:
        config = self.config
        close = frame["close"]

        delta = close.diff()

        gains = delta.clip(lower=0.0)
        losses = -delta.clip(upper=0.0)

        average_gain = gains.ewm(
            alpha=1.0 / config.rsi_length,
            adjust=False,
            min_periods=config.rsi_length,
        ).mean()

        average_loss = losses.ewm(
            alpha=1.0 / config.rsi_length,
            adjust=False,
            min_periods=config.rsi_length,
        ).mean()

        relative_strength = (
            average_gain
            / average_loss.replace(0.0, np.nan)
        )

        frame["RSI"] = (
            100.0
            - (100.0 / (1.0 + relative_strength))
        )

        frame["ROC"] = close.pct_change(
            config.roc_length
        )

        frame["RETURN_1"] = close.pct_change(1)
        frame["RETURN_3"] = close.pct_change(3)
        frame["RETURN_6"] = close.pct_change(6)

        frame["MOMENTUM_10"] = (
            close
            - close.shift(config.roc_length)
        ) / close.shift(config.roc_length)

        return frame

    def _add_volatility_features(
        self,
        frame: pd.DataFrame,
    ) -> pd.DataFrame:
        config = self.config

        previous_close = frame["close"].shift(1)

        true_range = pd.concat(
            [
                frame["high"] - frame["low"],
                (frame["high"] - previous_close).abs(),
                (frame["low"] - previous_close).abs(),
            ],
            axis=1,
        ).max(axis=1)

        frame["TR"] = true_range

        frame["ATR"] = true_range.ewm(
            alpha=1.0 / config.atr_length,
            adjust=False,
            min_periods=config.atr_length,
        ).mean()

        frame["ATR_PCT"] = (
            frame["ATR"] / frame["close"]
        )

        atr_baseline = frame["ATR"].rolling(
            config.atr_length,
            min_periods=config.atr_length,
        ).mean()

        frame["ATR_RATIO"] = (
            frame["ATR"]
            / atr_baseline.replace(0.0, np.nan)
        )

        frame["BODY"] = (
            frame["close"] - frame["open"]
        )

        frame["BODY_PCT"] = (
            frame["BODY"] / frame["open"]
        )

        frame["RANGE"] = (
            frame["high"] - frame["low"]
        )

        frame["RANGE_PCT"] = (
            frame["RANGE"] / frame["open"]
        )

        frame["UPPER_WICK"] = (
            frame["high"]
            - frame[["open", "close"]].max(axis=1)
        )

        frame["LOWER_WICK"] = (
            frame[["open", "close"]].min(axis=1)
            - frame["low"]
        )

        safe_range = frame["RANGE"].replace(
            0.0,
            np.nan,
        )

        frame["UPPER_WICK_PCT"] = (
            frame["UPPER_WICK"] / safe_range
        )

        frame["LOWER_WICK_PCT"] = (
            frame["LOWER_WICK"] / safe_range
        )

        frame["BULLISH"] = (
            frame["close"] > frame["open"]
        ).astype(int)

        frame["BEARISH"] = (
            frame["close"] < frame["open"]
        ).astype(int)

        frame["DOJI"] = (
            frame["BODY"].abs()
            <= frame["RANGE"] * 0.10
        ).astype(int)

        return frame

    def _add_volume_features(
        self,
        frame: pd.DataFrame,
    ) -> pd.DataFrame:
        length = self.config.volume_length

        frame["VOL_SMA20"] = frame["volume"].rolling(
            length,
            min_periods=length,
        ).mean()

        frame["VOL_RATIO"] = (
            frame["volume"]
            / frame["VOL_SMA20"].replace(0.0, np.nan)
        )

        volume_std = frame["volume"].rolling(
            length,
            min_periods=length,
        ).std(ddof=0)

        frame["VOL_ZSCORE"] = (
            frame["volume"] - frame["VOL_SMA20"]
        ) / volume_std.replace(0.0, np.nan)

        frame["PRICE_VOLUME_IMPULSE"] = (
            frame["RETURN_1"] * frame["VOL_RATIO"]
        )

        return frame

    def _add_structure_features(
        self,
        frame: pd.DataFrame,
    ) -> pd.DataFrame:
        length = self.config.structure_length

        frame["HIGH20"] = frame["high"].rolling(
            length,
            min_periods=length,
        ).max()

        frame["LOW20"] = frame["low"].rolling(
            length,
            min_periods=length,
        ).min()

        frame["DIST_HIGH20"] = (
            frame["HIGH20"] - frame["close"]
        ) / frame["close"]

        frame["DIST_LOW20"] = (
            frame["close"] - frame["LOW20"]
        ) / frame["close"]

        prior_high = frame["HIGH20"].shift(1)
        prior_low = frame["LOW20"].shift(1)

        frame["BREAK_HIGH20"] = (
            frame["high"] > prior_high
        ).astype(int)

        frame["BREAK_LOW20"] = (
            frame["low"] < prior_low
        ).astype(int)

        structure_range = (
            frame["HIGH20"] - frame["LOW20"]
        ).replace(0.0, np.nan)

        frame["RANGE_POSITION"] = (
            frame["close"] - frame["LOW20"]
        ) / structure_range

        return frame

    def _add_po3_features(
        self,
        frame: pd.DataFrame,
    ) -> pd.DataFrame:
        config = self.config
        length = config.accumulation_length

        raw_high = frame["high"].rolling(
            length,
            min_periods=length,
        ).max()

        raw_low = frame["low"].rolling(
            length,
            min_periods=length,
        ).min()

        accumulation_range = raw_high - raw_low

        frame["ACC_HIGH"] = raw_high
        frame["ACC_LOW"] = raw_low
        frame["ACC_RANGE"] = accumulation_range
        frame["ACC_RANGE_PCT"] = (
            accumulation_range
            / frame["close"]
        )

        frame["ACC_ATR_RATIO"] = (
            accumulation_range
            / frame["ATR"].replace(0.0, np.nan)
        )

        frame["ACC_EXPANDED_HIGH"] = (
            raw_high
            + (
                frame["ATR"]
                * config.accumulation_expand_multiplier
            )
        )

        frame["ACC_EXPANDED_LOW"] = (
            raw_low
            - (
                frame["ATR"]
                * config.accumulation_expand_multiplier
            )
        )

        frame["DIST_ACC_HIGH"] = (
            frame["ACC_EXPANDED_HIGH"]
            - frame["close"]
        ) / frame["close"]

        frame["DIST_ACC_LOW"] = (
            frame["close"]
            - frame["ACC_EXPANDED_LOW"]
        ) / frame["close"]

        frame["INSIDE_ACC"] = (
            (frame["close"] <= frame["ACC_EXPANDED_HIGH"])
            & (frame["close"] >= frame["ACC_EXPANDED_LOW"])
        ).astype(int)

        frame["ACCUMULATION_VALID"] = (
            accumulation_range
            <= (
                frame["ATR"]
                * config.accumulation_atr_multiplier
            )
        ).astype(int)

        frame["ACCUMULATION_BARS"] = (
            frame["ACCUMULATION_VALID"]
            .groupby(
                (
                    frame["ACCUMULATION_VALID"]
                    != frame["ACCUMULATION_VALID"].shift()
                ).cumsum()
            )
            .cumsum()
            * frame["ACCUMULATION_VALID"]
        )

        self._apply_po3_state_machine(frame)

        return frame

    def _apply_po3_state_machine(
        self,
        frame: pd.DataFrame,
    ) -> None:
        config = self.config
        count = len(frame)

        state_values = np.zeros(
            count,
            dtype=np.int8,
        )

        long_values = np.zeros(
            count,
            dtype=np.int8,
        )

        short_values = np.zeros(
            count,
            dtype=np.int8,
        )

        signal_values = np.zeros(
            count,
            dtype=np.int8,
        )

        manipulation_up = np.zeros(
            count,
            dtype=np.int8,
        )

        manipulation_down = np.zeros(
            count,
            dtype=np.int8,
        )

        manipulation_direction = np.zeros(
            count,
            dtype=np.int8,
        )

        manipulation_distance = np.full(
            count,
            np.nan,
            dtype=float,
        )

        manipulation_atr = np.full(
            count,
            np.nan,
            dtype=float,
        )

        sweep_high = np.zeros(
            count,
            dtype=np.int8,
        )

        sweep_low = np.zeros(
            count,
            dtype=np.int8,
        )

        breakout_force = np.full(
            count,
            np.nan,
            dtype=float,
        )

        distribution_body_atr = np.full(
            count,
            np.nan,
            dtype=float,
        )

        distribution_range_atr = np.full(
            count,
            np.nan,
            dtype=float,
        )

        state = 0

        active_high = np.nan
        active_low = np.nan
        active_atr = np.nan
        direction = 0

        high_values = frame["high"].to_numpy(
            dtype=float
        )

        low_values = frame["low"].to_numpy(
            dtype=float
        )

        close_values = frame["close"].to_numpy(
            dtype=float
        )

        atr_values = frame["ATR"].to_numpy(
            dtype=float
        )

        acc_high_values = frame[
            "ACC_EXPANDED_HIGH"
        ].to_numpy(dtype=float)

        acc_low_values = frame[
            "ACC_EXPANDED_LOW"
        ].to_numpy(dtype=float)

        accumulation_valid = frame[
            "ACCUMULATION_VALID"
        ].to_numpy(dtype=np.int8)

        body_values = frame["BODY"].to_numpy(
            dtype=float
        )

        range_values = frame["RANGE"].to_numpy(
            dtype=float
        )

        for index in range(count):
            atr = atr_values[index]

            if not np.isfinite(atr) or atr <= 0:
                continue

            high_breakout = (
                close_values[index]
                if config.breakout_method.lower() == "close"
                else high_values[index]
            )

            low_breakout = (
                close_values[index]
                if config.breakout_method.lower() == "close"
                else low_values[index]
            )

            if state == 0:
                if accumulation_valid[index] == 1:
                    active_high = acc_high_values[index]
                    active_low = acc_low_values[index]
                    active_atr = atr
                    direction = 0
                    state = 1

            elif state == 1:
                state_values[index] = 1

                if (
                    high_breakout > active_high
                    or low_breakout < active_low
                ):
                    state = 2

            elif state == 2:
                state_values[index] = 2

                upward_threshold = (
                    active_high
                    + (
                        active_atr
                        * config.manipulation_atr_multiplier
                    )
                )

                downward_threshold = (
                    active_low
                    - (
                        active_atr
                        * config.manipulation_atr_multiplier
                    )
                )

                if high_breakout > upward_threshold:
                    direction = 1
                    manipulation_up[index] = 1
                    manipulation_direction[index] = 1
                    sweep_high[index] = 1

                    distance = (
                        high_breakout - active_high
                    )

                    manipulation_distance[index] = distance
                    manipulation_atr[index] = (
                        distance / active_atr
                    )

                    breakout_force[index] = (
                        distance / active_atr
                    )

                    state = 3

                elif low_breakout < downward_threshold:
                    direction = -1
                    manipulation_down[index] = 1
                    manipulation_direction[index] = -1
                    sweep_low[index] = 1

                    distance = (
                        active_low - low_breakout
                    )

                    manipulation_distance[index] = distance
                    manipulation_atr[index] = (
                        distance / active_atr
                    )

                    breakout_force[index] = (
                        distance / active_atr
                    )

                    state = 3

            elif state == 3:
                state_values[index] = 3
                manipulation_direction[index] = direction

                distribution_body_atr[index] = (
                    abs(body_values[index])
                    / atr
                )

                distribution_range_atr[index] = (
                    range_values[index]
                    / atr
                )

                if direction == -1:
                    long_values[index] = 1
                    signal_values[index] = 1

                elif direction == 1:
                    short_values[index] = 1
                    signal_values[index] = -1

                state = 0
                direction = 0
                active_high = np.nan
                active_low = np.nan
                active_atr = np.nan

        frame["MANIPULATION_UP"] = manipulation_up
        frame["MANIPULATION_DOWN"] = manipulation_down
        frame["MANIPULATION_DIRECTION"] = (
            manipulation_direction
        )
        frame["MANIPULATION_DISTANCE"] = (
            manipulation_distance
        )
        frame["MANIPULATION_ATR"] = manipulation_atr
        frame["LIQUIDITY_SWEEP_HIGH"] = sweep_high
        frame["LIQUIDITY_SWEEP_LOW"] = sweep_low

        frame["PO3_STATE"] = state_values
        frame["PO3_LONG_SETUP"] = long_values
        frame["PO3_SHORT_SETUP"] = short_values
        frame["PO3_SIGNAL"] = signal_values

        frame["BREAKOUT_FORCE"] = breakout_force
        frame["DISTRIBUTION_BODY_ATR"] = (
            distribution_body_atr
        )
        frame["DISTRIBUTION_RANGE_ATR"] = (
            distribution_range_atr
        )

        frame[
            "MANIPULATION_DIRECTION"
        ] = (
            frame["MANIPULATION_DIRECTION"]
            .replace(0, np.nan)
            .ffill(limit=3)
            .fillna(0)
            .astype(int)
        )

    @staticmethod
    def _add_time_features(
        frame: pd.DataFrame,
    ) -> pd.DataFrame:
        if "timestamp" not in frame.columns:
            frame["HOUR"] = 0
            frame["DAY_OF_WEEK"] = 0
            frame["ASIA_SESSION"] = 0
            frame["LONDON_SESSION"] = 0
            frame["NEW_YORK_SESSION"] = 0

            return frame

        timestamp = frame["timestamp"]

        frame["HOUR"] = timestamp.dt.hour
        frame["DAY_OF_WEEK"] = timestamp.dt.dayofweek

        frame["ASIA_SESSION"] = (
            frame["HOUR"].between(0, 7)
        ).astype(int)

        frame["LONDON_SESSION"] = (
            frame["HOUR"].between(7, 15)
        ).astype(int)

        frame["NEW_YORK_SESSION"] = (
            frame["HOUR"].between(13, 21)
        ).astype(int)

        return frame