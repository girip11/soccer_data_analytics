"""Module providing utility functions to compute the ball trajectory.

I thought of two approaches for computing the length of the ball trajectory.

1. Find the distance between the player positions in the successive events.
This is relatively cheaper to compute but still provides a good approximation.

2. For every event between the start event and end event, calculate how many
frames(40ms apart) would exist and note the player with the ball at that timeframe.
This involves too much computation given player position is tracked every 40ms.

I went ahead with approach 1.
"""
from typing import Tuple

import numpy as np
import pandas as pd
from scipy.spatial import distance

from metadata import Event
from utils.event_utils import get_event_id_for, get_events_between


def compute_ball_trajectory_between_events(
    events_df: pd.DataFrame, event1: Tuple[str, int], event2: Tuple[str, int]
) -> float:
    """Compute the length of the ball trajectory between the given events

    Parameters
    ----------
    events_df : pd.DataFrame
        Events in the soccer game
    event1 : Tuple[str, int]
        Start event
    event2 : Tuple[str, int]
        End event

    Returns
    -------
    float
        Length of the ball trajectory in meters.
    """
    event1_id: int = get_event_id_for(events_df, event_name=event1[0], n=event1[1])
    event2_id: int = get_event_id_for(events_df, event_name=event2[0], n=event2[1])

    subevents_df: pd.DataFrame = get_events_between(events_df, event1_id, event2_id)
    subevents_df.sort_values(by=Event.event_id, ascending=True, inplace=True)

    ball_trajectory_length: float = 0.0

    for window in subevents_df.rolling(window=2):
        if len(window) == 2:
            coords_1 = [(window.iloc[0]["x"], window.iloc[0]["y"])]
            coords_2 = [(window.iloc[1]["x"], window.iloc[1]["y"])]
            ball_trajectory_length += distance.cdist(coords_1, coords_2, metric="euclidean")[0, 0]

    return np.round(ball_trajectory_length / 100.0, 2)
