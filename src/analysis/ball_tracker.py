from typing import List, Tuple

import numpy as np
import pandas as pd
from scipy.spatial import distance

from metadata import TrackedPosition
from utils.event_utils import get_current_next_event_pairs, get_event_id_for, get_events_between


def compute_ball_trajectory_between_events(
    events_df: pd.DataFrame, event1: Tuple[str, int], event2: Tuple[str, int]
) -> float:
    event1_id: int = get_event_id_for(events_df, event_name=event1[0], n=event1[1])
    event2_id: int = get_event_id_for(events_df, event_name=event2[0], n=event2[1])

    subevents_df: pd.DataFrame = get_events_between(events_df, event1_id, event2_id)

    required_cols: List[str] = [TrackedPosition.x, TrackedPosition.y]
    current_next_event_pairs: pd.DataFrame = get_current_next_event_pairs(
        subevents_df, current_event_cols=required_cols, next_event_cols=required_cols
    )

    def compute_distance(row: pd.Series) -> pd.Series:
        coords_1 = [(row["x"], row["y"])]
        coords_2 = [(row["x_next"], row["y_next"])]
        return pd.Series(distance.cdist(coords_1, coords_2, metric="euclidean")[0])

    return np.round(
        current_next_event_pairs.apply(compute_distance, axis=1, raw=False).sum() / 100.0,
        2,
    )[0]
