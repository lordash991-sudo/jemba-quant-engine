from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Final

import numpy as np
import pandas as pd


class PO3Label(IntEnum):
    """
    Resultado supervisado de una oportunidad PO3.
    """

    STOP_LOSS = -1
    EXPIRED = 0
    TAKE_PROFIT = 1


@dataclass(frozen=True)
class PO3LabelConfig:
    """
    Parámetros para etiquetar señales PO3.

    El objetivo se calcula usando múltiplos de ATR desde
    el precio de entrada de la señal.

    Ejemplo LONG:
        stop_loss = entry - ATR * stop_atr
        take_profit = entry + ATR * target_atr

    Ejemplo SHORT:
        stop_loss = entry + ATR * stop_atr
        take_profit = entry - ATR * target_atr
    """

    horizon_bars: int = 24
    stop_atr: float = 1.0
    target_atr: float = 2.0
    entry_mode: str = "close"
    ambiguous_policy: str = "stop_first"

    def __post_init__(self) -> None:
        if self.horizon_bars < 1:
            raise ValueError(
                "HORIZON_BARS_MUST_BE_AT_LEAST_1"
            )

        if self.stop_atr <= 0:
            raise ValueError(
                "STOP_ATR_MUST_BE_POSITIVE"
            )

        if self.target_atr <= 0:
            raise ValueError(
                "TARGET_ATR_MUST_BE_POSITIVE"
            )

        entry_mode = self.entry_mode.strip().lower()

        if entry_mode not in {
            "close",
            "next_open",
        }:
            raise ValueError(
                "ENTRY_MODE_MUST_BE_CLOSE_OR_NEXT_OPEN"
            )

        policy = self.ambiguous_policy.strip().lower()

        if policy not in {
            "stop_first",
            "target_first",
            "expired",
        }:
            raise ValueError(
                "AMBIGUOUS_POLICY_INVALID"
            )


class PO3LabelGenerator:
    """
    Genera etiquetas TP, SL o EXPIRED para señales PO3.

    No genera señales.
    No ejecuta operaciones.
    No usa información anterior a la señal para determinar
    el resultado.
    """

    REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
        "open",
        "high",
        "low",
        "close",
        "ATR",
        "PO3_SIGNAL",
    )

    OUTPUT_COLUMNS: Final[tuple[str, ...]] = (
        "LABEL",
        "LABEL_NAME",
        "ENTRY_PRICE",
        "STOP_LOSS",
        "TAKE_PROFIT",
        "EXIT_PRICE",
        "EXIT_BAR_INDEX",
        "BARS_TO_EXIT",
        "RETURN_PCT",
        "R_MULTIPLE",
        "MFE_PCT",
        "MAE_PCT",
        "HIT_TP",
        "HIT_SL",
        "EXPIRED",
        "AMBIGUOUS_HIT",
    )

    def __init__(
        self,
        config: PO3LabelConfig | None = None,
    ) -> None:
        self.config = config or PO3LabelConfig()

    def generate(
        self,
        features: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Añade las etiquetas al DataFrame de features.

        Solo evalúa filas con PO3_SIGNAL igual a 1 o -1.
        Las demás filas permanecen sin etiqueta.
        """

        frame = self._validate_and_prepare(features)

        result = frame.copy()

        for column in self.OUTPUT_COLUMNS:
            if column == "LABEL_NAME":
                result[column] = pd.Series(
                    index=result.index,
                    dtype="object",
                )
            else:
                result[column] = np.nan

        signal_indices = result.index[
            result["PO3_SIGNAL"].isin([-1, 1])
        ].tolist()

        for signal_index in signal_indices:
            outcome = self._label_signal(
                result,
                signal_index=signal_index,
            )

            if outcome is None:
                continue

            for key, value in outcome.items():
                result.at[signal_index, key] = value

        result["LABEL"] = pd.to_numeric(
            result["LABEL"],
            errors="coerce",
        )

        for column in (
            "HIT_TP",
            "HIT_SL",
            "EXPIRED",
            "AMBIGUOUS_HIT",
        ):
            result[column] = pd.to_numeric(
                result[column],
                errors="coerce",
            )

        return result

    def training_dataset(
        self,
        features: pd.DataFrame,
        *,
        include_expired: bool = True,
    ) -> pd.DataFrame:
        """
        Devuelve únicamente las filas señaladas y etiquetadas.
        """

        labelled = self.generate(features)

        dataset = labelled[
            labelled["LABEL"].notna()
        ].copy()

        if not include_expired:
            dataset = dataset[
                dataset["LABEL"]
                != int(PO3Label.EXPIRED)
            ].copy()

        return dataset.reset_index(drop=True)

    def _validate_and_prepare(
        self,
        features: pd.DataFrame,
    ) -> pd.DataFrame:
        if not isinstance(features, pd.DataFrame):
            raise TypeError(
                "FEATURES_MUST_BE_A_PANDAS_DATAFRAME"
            )

        if features.empty:
            raise ValueError(
                "FEATURES_DATAFRAME_IS_EMPTY"
            )

        frame = features.copy()

        missing = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in frame.columns
        ]

        if missing:
            raise ValueError(
                f"MISSING_LABEL_COLUMNS: {missing}"
            )

        numeric_columns = (
            "open",
            "high",
            "low",
            "close",
            "ATR",
            "PO3_SIGNAL",
        )

        for column in numeric_columns:
            frame[column] = pd.to_numeric(
                frame[column],
                errors="coerce",
            )

        frame.reset_index(
            drop=True,
            inplace=True,
        )

        return frame

    def _label_signal(
        self,
        frame: pd.DataFrame,
        *,
        signal_index: int,
    ) -> dict[str, float | int | str] | None:
        config = self.config

        signal = int(
            frame.at[
                signal_index,
                "PO3_SIGNAL",
            ]
        )

        atr = float(
            frame.at[
                signal_index,
                "ATR",
            ]
        )

        if (
            signal not in {-1, 1}
            or not np.isfinite(atr)
            or atr <= 0
        ):
            return None

        if config.entry_mode.lower() == "next_open":
            entry_index = signal_index + 1

            if entry_index >= len(frame):
                return None

            entry = float(
                frame.at[
                    entry_index,
                    "open",
                ]
            )

            evaluation_start = entry_index

        else:
            entry_index = signal_index

            entry = float(
                frame.at[
                    signal_index,
                    "close",
                ]
            )

            evaluation_start = signal_index + 1

        if not np.isfinite(entry) or entry <= 0:
            return None

        if signal == 1:
            stop_loss = (
                entry
                - atr * config.stop_atr
            )

            take_profit = (
                entry
                + atr * config.target_atr
            )

        else:
            stop_loss = (
                entry
                + atr * config.stop_atr
            )

            take_profit = (
                entry
                - atr * config.target_atr
            )

        evaluation_end = min(
            evaluation_start
            + config.horizon_bars,
            len(frame),
        )

        if evaluation_start >= evaluation_end:
            return None

        future = frame.iloc[
            evaluation_start:evaluation_end
        ]

        maximum_favourable = 0.0
        maximum_adverse = 0.0

        for current_index, row in future.iterrows():
            high = float(row["high"])
            low = float(row["low"])
            close = float(row["close"])

            if signal == 1:
                target_hit = high >= take_profit
                stop_hit = low <= stop_loss

                favourable_move = (
                    high - entry
                ) / entry

                adverse_move = (
                    low - entry
                ) / entry

            else:
                target_hit = low <= take_profit
                stop_hit = high >= stop_loss

                favourable_move = (
                    entry - low
                ) / entry

                adverse_move = (
                    entry - high
                ) / entry

            maximum_favourable = max(
                maximum_favourable,
                favourable_move,
            )

            maximum_adverse = min(
                maximum_adverse,
                adverse_move,
            )

            if target_hit and stop_hit:
                return self._ambiguous_result(
                    signal=signal,
                    entry=entry,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    exit_index=current_index,
                    entry_index=entry_index,
                    maximum_favourable=maximum_favourable,
                    maximum_adverse=maximum_adverse,
                )

            if target_hit:
                return self._build_result(
                    label=PO3Label.TAKE_PROFIT,
                    signal=signal,
                    entry=entry,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    exit_price=take_profit,
                    exit_index=current_index,
                    entry_index=entry_index,
                    maximum_favourable=maximum_favourable,
                    maximum_adverse=maximum_adverse,
                    ambiguous=False,
                )

            if stop_hit:
                return self._build_result(
                    label=PO3Label.STOP_LOSS,
                    signal=signal,
                    entry=entry,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    exit_price=stop_loss,
                    exit_index=current_index,
                    entry_index=entry_index,
                    maximum_favourable=maximum_favourable,
                    maximum_adverse=maximum_adverse,
                    ambiguous=False,
                )

        final_index = int(
            future.index[-1]
        )

        final_close = float(
            frame.at[
                final_index,
                "close",
            ]
        )

        return self._build_result(
            label=PO3Label.EXPIRED,
            signal=signal,
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            exit_price=final_close,
            exit_index=final_index,
            entry_index=entry_index,
            maximum_favourable=maximum_favourable,
            maximum_adverse=maximum_adverse,
            ambiguous=False,
        )

    def _ambiguous_result(
        self,
        *,
        signal: int,
        entry: float,
        stop_loss: float,
        take_profit: float,
        exit_index: int,
        entry_index: int,
        maximum_favourable: float,
        maximum_adverse: float,
    ) -> dict[str, float | int | str]:
        policy = (
            self.config
            .ambiguous_policy
            .strip()
            .lower()
        )

        if policy == "target_first":
            label = PO3Label.TAKE_PROFIT
            exit_price = take_profit

        elif policy == "expired":
            label = PO3Label.EXPIRED
            exit_price = entry

        else:
            label = PO3Label.STOP_LOSS
            exit_price = stop_loss

        return self._build_result(
            label=label,
            signal=signal,
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            exit_price=exit_price,
            exit_index=exit_index,
            entry_index=entry_index,
            maximum_favourable=maximum_favourable,
            maximum_adverse=maximum_adverse,
            ambiguous=True,
        )

    @staticmethod
    def _build_result(
        *,
        label: PO3Label,
        signal: int,
        entry: float,
        stop_loss: float,
        take_profit: float,
        exit_price: float,
        exit_index: int,
        entry_index: int,
        maximum_favourable: float,
        maximum_adverse: float,
        ambiguous: bool,
    ) -> dict[str, float | int | str]:
        if signal == 1:
            return_pct = (
                exit_price - entry
            ) / entry

        else:
            return_pct = (
                entry - exit_price
            ) / entry

        risk_distance = abs(
            entry - stop_loss
        )

        if risk_distance <= 0:
            r_multiple = 0.0
        else:
            signed_profit = (
                exit_price - entry
                if signal == 1
                else entry - exit_price
            )

            r_multiple = (
                signed_profit
                / risk_distance
            )

        return {
            "LABEL": int(label),
            "LABEL_NAME": label.name,
            "ENTRY_PRICE": float(entry),
            "STOP_LOSS": float(stop_loss),
            "TAKE_PROFIT": float(take_profit),
            "EXIT_PRICE": float(exit_price),
            "EXIT_BAR_INDEX": int(exit_index),
            "BARS_TO_EXIT": int(
                exit_index - entry_index + 1
            ),
            "RETURN_PCT": float(return_pct),
            "R_MULTIPLE": float(r_multiple),
            "MFE_PCT": float(
                maximum_favourable
            ),
            "MAE_PCT": float(
                maximum_adverse
            ),
            "HIT_TP": int(
                label
                == PO3Label.TAKE_PROFIT
            ),
            "HIT_SL": int(
                label
                == PO3Label.STOP_LOSS
            ),
            "EXPIRED": int(
                label
                == PO3Label.EXPIRED
            ),
            "AMBIGUOUS_HIT": int(
                ambiguous
            ),
        }