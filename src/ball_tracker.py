import numpy as np
import pandas as pd
from scipy.spatial import distance

from metadata import Event, TrackedPosition


def get_event_id_for(events_df: pd.DataFrame, *, event_name: str, n: int) -> int:
    event_col: str = Event.event
    event_filter: pd.Series[bool] = events_df[event_col] == event_name
    return events_df.loc[event_filter, Event.event_id].iloc[n]


def get_events_between(
    events_df: pd.DataFrame, event_id1: int, event_id2: int
) -> pd.DataFrame:
    filter_criteria: pd.Series = (events_df[Event.event_id] > event_id1) & (
        events_df[Event.event_id] < event_id2
    )

    return events_df.loc[filter_criteria]


def compute_ball_trajectory(events_df: pd.DataFrame) -> float:
    tmp_events_df: pd.DataFrame = pd.DataFrame(events_df)
    next_event: str = "next_event"
    tmp_events_df[next_event] = tmp_events_df[Event.event_id].apply(lambda e: e + 1)

    current_next_event_pairs: pd.DataFrame = tmp_events_df.merge(
        tmp_events_df,
        how="inner",
        left_on=[Event.event_id],
        right_on=[next_event],
        suffixes=(None, "_next"),
        validate="1:1",
    ).filter(
        [
            TrackedPosition.x,
            TrackedPosition.y,
            f"{TrackedPosition.x}_next",
            f"{TrackedPosition.y}_next",
        ]
    )

    def compute_distance(row: pd.Series) -> pd.Series:
        coords_1 = [(row["x"], row["y"])]
        coords_2 = [(row["x_next"], row["y_next"])]
        return pd.Series(distance.cdist(coords_1, coords_2, metric="euclidean")[0])

    return np.round(
        current_next_event_pairs.apply(compute_distance, axis=1, raw=False).sum()
        / 100.0,
        2,
    )[0]
