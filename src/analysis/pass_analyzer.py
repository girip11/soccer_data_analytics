from typing import ClassVar, Tuple

import pandas as pd
from pandas.api.types import pandas_dtype

from metadata import Event, EventType
from utils.event_utils import get_current_next_event_pairs


class PassingStatistics:
    _next_event: ClassVar[str] = "next_event"

    _PASS_SUCCESS: ClassVar[int] = 1
    _PASS_FAILURE: ClassVar[int] = 0
    _NOT_A_PASS: ClassVar[int] = -1

    @staticmethod
    def _set_pass_status(row: pd.Series) -> pd.Series:
        if row[Event.event] == EventType.PASS or row[Event.event] == EventType.CROSS:
            if row["event_next"] == EventType.RECEPTION:
                return pd.Series(PassingStatistics._PASS_SUCCESS)
            else:
                return pd.Series(PassingStatistics._PASS_FAILURE)

        return pd.Series(PassingStatistics._NOT_A_PASS)

    def add_pass_status(self, events_df: pd.DataFrame) -> None:
        current_next_event_pairs = get_current_next_event_pairs(
            events_df, current_event_cols=Event.columns(), next_event_cols=[Event.event]
        )
        events_df["pass_status"] = (
            current_next_event_pairs.apply(PassingStatistics._set_pass_status, axis=1, raw=False)
            .astype(pandas_dtype("Int8"))
            .iloc[:, 0]
        )

    def player_with_most_passes(self, events_df: pd.DataFrame) -> Tuple[int, int]:
        pass_events_filter = (events_df[Event.event] == EventType.PASS) | (
            events_df[Event.event] == EventType.CROSS
        )

        player_id, total_passes = (
            events_df[pass_events_filter]
            .groupby(Event.player_id, as_index=False)
            .agg(total_passes=("pass_status", "count"))
            .nlargest(1, "total_passes")
            .iloc[0]
            .values
        )

        return (player_id, total_passes)

    @staticmethod
    def _pass_completion_rate(pass_status: pd.Series) -> float:
        return (pass_status.sum() / pass_status.count()) * 100.0

    def player_with_max_pass_completion_rate(self, events_df: pd.DataFrame) -> Tuple[int, int, int]:
        pass_events_filter = (events_df[Event.event] == EventType.PASS) | (
            events_df[Event.event] == EventType.CROSS
        )

        player_id, compl_rate, total_passes = (
            events_df[pass_events_filter]
            .groupby(Event.player_id, as_index=False)
            .agg(
                total_passes=("pass_status", "count"),
                completion_rate=(
                    "pass_status",
                    PassingStatistics._pass_completion_rate,
                ),
            )
            .sort_values(by=["completion_rate", "total_passes"], ascending=False)
            .iloc[0]
            .values
        )

        return (int(player_id), compl_rate, total_passes)
