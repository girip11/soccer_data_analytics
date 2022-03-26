from typing import List

import numpy as np
import pandas as pd
from pandas.api.types import pandas_dtype

from metadata import Event, TrackedPosition


def _convert_time_to_ms(time_in_sec: float, start_time_in_ms: int) -> int:
    return int(time_in_sec * 1000) - start_time_in_ms


def convert_event_time_to_ms(events_df: pd.DataFrame) -> None:
    time_col: str = Event.time
    start_time_in_ms: int = _convert_time_to_ms(events_df[time_col].min(), 0)
    events_df[time_col] = (
        events_df[time_col]
        .apply(_convert_time_to_ms, start_time_in_ms=start_time_in_ms)
        .astype(pandas_dtype("Int64"))
    )


def add_position_to_event(events_df: pd.DataFrame, positions_df: pd.DataFrame) -> pd.DataFrame:
    time_col: str = Event.time
    frame_number: str = "frame_number"
    event_positions_df: pd.DataFrame

    # Pick the time frame that is closest to the event.
    events_df[frame_number] = (
        events_df[time_col].apply(lambda t: np.round(t / 40)).astype(pandas_dtype("Int64"))
    )

    positions_df[frame_number] = (
        positions_df[time_col].apply(lambda t: t // 40).astype(pandas_dtype("Int64"))
    )

    try:
        event_positions_df = events_df.merge(
            positions_df,
            how="left",
            on=[frame_number, Event.player_id],
            suffixes=(None, "_r"),
            validate="m:1",
        ).filter(Event.columns() + [TrackedPosition.x, TrackedPosition.y])
    finally:
        events_df.drop(frame_number, axis=1, inplace=True)
        positions_df.drop(frame_number, axis=1, inplace=True)

    return event_positions_df


def is_event_like_df(df: pd.DataFrame) -> bool:
    return all(col in df.columns for col in Event.columns())


def get_event_id_for(events_like_df: pd.DataFrame, event_name: str, n: int = 0) -> int:
    if not is_event_like_df(events_like_df):
        raise ValueError("Required a dataframe with all columns of Event")

    event_filter: pd.Series[bool] = events_like_df[Event.event] == event_name
    return events_like_df.loc[event_filter, Event.event_id].iloc[n]


def get_events_between(
    events_like_df: pd.DataFrame, event_id1: int, event_id2: int
) -> pd.DataFrame:
    if not is_event_like_df(events_like_df):
        raise ValueError("Required a dataframe with all columns of Event")

    event_id_col: str = Event.event_id
    filter_criteria: pd.Series = (events_like_df[event_id_col] > event_id1) & (
        events_like_df[event_id_col] < event_id2
    )

    return pd.DataFrame(events_like_df.loc[filter_criteria])


def get_current_next_event_pairs(
    events_like_df: pd.DataFrame, *, current_event_cols: List[str], next_event_cols: List[str]
) -> pd.DataFrame:

    if not is_event_like_df(events_like_df):
        raise ValueError("Required a dataframe with all columns of Event")

    next_event: str = "next_event"
    events_like_df[next_event] = events_like_df[Event.event_id].apply(lambda e: e + 1)

    right_df: pd.DataFrame = events_like_df[[Event.event_id] + next_event_cols]
    current_next_event_pairs: pd.DataFrame = events_like_df.merge(
        right_df,
        how="inner",
        left_on=[next_event],
        right_on=[Event.event_id],
        suffixes=(None, "_next"),
        validate="1:1",
    ).filter(current_event_cols + [f"{col}_next" for col in next_event_cols])

    events_like_df.drop(next_event, axis=1, inplace=True)
    return current_next_event_pairs
