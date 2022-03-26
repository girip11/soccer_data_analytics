"""Module providing insights into player's passing.

Observation: A successful pass event can be followed by

1. pass to another player of the same team in case of freekick pass
2. reception by another player of the same team
3. clearance followed by reception by another player of same team
I am assuming freekick pass should also be counted.

Observation: A successful cross event can be followed by
1. clearance followed by reception by another player of same team
"""

from enum import Enum
from typing import Mapping, Tuple

import numpy as np
import pandas as pd

from metadata import Event, EventType


class PassStatus(Enum):
    Success = 1
    Failure = 0
    Not_A_Pass = -1


def is_short_pass_completed(pass_events: pd.DataFrame) -> bool:
    """Indicates if the short pass is completed.

    Short passes are usually followed by either another Pass or Reception event
    A short pass is considered completed if the pass is received by another player
    in the same team as the passing player.

    Parameters
    ----------
    pass_events : pd.DataFrame
        Window of events following the pass
    Returns
    -------
    bool
        True if the pass is completed.
    Raises
    ------
    ValueError
        When pass_events dataframe does not contain sufficient events
    ValueError
        When the first event is not a type of Pass event
    """
    if len(pass_events) < 2:
        raise ValueError("Need atleast 2 events to conclude the short pass status.")

    # Not sure if there can be cross with just reception. But handling it anyway
    if pass_events.iloc[0][Event.event] not in [EventType.PASS, EventType.CROSS]:
        raise ValueError("Expected the first event to be a pass or cross event")

    return all(
        [
            pass_events.iloc[1][Event.event] in [EventType.PASS, EventType.RECEPTION],
            # passing and receiving by the same team
            pass_events.iloc[0][Event.team_id] == pass_events.iloc[1][Event.team_id],
        ]
    )


def is_long_pass_completed(pass_events: pd.DataFrame) -> bool:
    """Indicates if the long pass is completed.

    Pass or Cross with clearance as the next event is considered as long pass.
    A long pass is considered completed if the pass is received by another player
    in the same team as the passing player immediately followint the pass event.

    Parameters
    ----------
    pass_events : pd.DataFrame
        Window of events following the pass
    Returns
    -------
    bool
        True if the pass is completed.
    Raises
    ------
    ValueError
        When pass_events dataframe does not contain sufficient events
    ValueError
        When the first event is not a type of Pass event
    """
    if len(pass_events) < 3:
        raise ValueError("Need atleast 3 events to conclude the long pass status.")

    if pass_events.iloc[0][Event.event] not in [EventType.PASS, EventType.CROSS]:
        raise ValueError("Expected the first event to be a pass or cross event")

    return all(
        [
            pass_events.iloc[1][Event.event] == EventType.CLEARANCE,
            pass_events.iloc[2][Event.event] == EventType.RECEPTION,
            # passing and receiving by the same team
            pass_events.iloc[0][Event.team_id] == pass_events.iloc[2][Event.team_id],
        ]
    )


PASS_STATUS_COL: str = "pass_status"


def compute_pass_status(events_df: pd.DataFrame) -> pd.DataFrame:
    """Compute if the pass or cross event is successful or misplaced.

    Parameters
    ----------
    events_df : pd.DataFrame
        Dataframe containing the events

    Returns
    -------
    pd.DataFrame
        Dataframe with the pass status column added.
    """
    events_df = events_df.assign(
        PASS_STATUS_COL=np.full(events_df.shape[0], PassStatus.Not_A_Pass.value, dtype="int8")
    )
    for window in events_df.rolling(window=3):
        if len(window) != 3:
            continue
        event_id_filter: pd.Series = events_df[Event.event_id] == window.iloc[0][Event.event_id]

        if window.iloc[0][Event.event] in [EventType.PASS, EventType.CROSS]:
            if any([is_short_pass_completed(window), is_long_pass_completed(window)]):
                events_df.loc[event_id_filter, PASS_STATUS_COL] = PassStatus.Success.value
            else:
                events_df.loc[event_id_filter, PASS_STATUS_COL] = PassStatus.Failure.value

    return events_df


def find_most_passing_player(events_df: pd.DataFrame) -> Tuple[int, int]:
    """Find the player who had done the most passsing.

    Parameters
    ----------
    events_df : pd.DataFrame

    Returns
    -------
    Tuple[int, int]
        (player_id, total passes made)
    """
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


def _pass_completion_rate(pass_status: pd.Series) -> float:
    """Compute the pass completion rate.

    Parameters
    ----------
    pass_status : pd.Series
        Status of all the passes made by the player
    Returns
    -------
    float
        player pass completion rate
    """
    return (pass_status.sum() / pass_status.count()) * 100.0


def find_most_pass_completing_player(events_df: pd.DataFrame) -> Tuple[int, float, int]:
    """Find the player with the highest pass completion rate

    Player Pass completion rate = (total successful passes / total pass ) * 100.0

    Parameters
    ----------
    events_df : pd.DataFrame

    Returns
    -------
    Tuple[int, int, int]
        (player_id, pass completion percentage, total passes made)
    """
    pass_events_filter = (events_df[Event.event] == EventType.PASS) | (
        events_df[Event.event] == EventType.CROSS
    )

    result: Mapping[str, float] = (
        events_df[pass_events_filter]
        .groupby(Event.player_id, as_index=False)
        .agg(
            total_passes=("pass_status", "count"),
            completion_rate=("pass_status", _pass_completion_rate),
        )
        .sort_values(by=["completion_rate", "total_passes"], ascending=False)
        .iloc[0]
        .to_dict()
    )

    return (int(result[Event.player_id]), result["completion_rate"], int(result["total_passes"]))
