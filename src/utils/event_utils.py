import numpy as np
import pandas as pd
from pandas.api.types import pandas_dtype

from metadata import Event, TrackedPosition


def _convert_time_to_ms(time_in_sec: float, start_time_in_ms: int) -> int:
    return int(time_in_sec * 1000) - start_time_in_ms


def convert_event_time_to_ms(events_df: pd.DataFrame) -> None:
    """Convert the time column in seconds to milliseconds

    Parameters
    ----------
    events_df : pd.DataFrame
        Events in the soccer game.
    """
    time_col: str = Event.time
    start_time_in_ms: int = _convert_time_to_ms(events_df[time_col].min(), 0)
    events_df[time_col] = (
        events_df[time_col]
        .apply(_convert_time_to_ms, start_time_in_ms=start_time_in_ms)
        .astype(pandas_dtype("Int64"))
    )


def add_position_to_event(events_df: pd.DataFrame, positions_df: pd.DataFrame) -> pd.DataFrame:
    """Add position of the player in the event to the dataframe.

    Parameters
    ----------
    events_df : pd.DataFrame
        Events in the game
    positions_df : pd.DataFrame
        Position of the players in the game

    Returns
    -------
    pd.DataFrame
        Events with the position of the players.
    """
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
    """Return True if the dataframe has all the columns of Event dataset

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    bool
    """
    return all(col in df.columns for col in Event.columns())


def get_event_id_for(events_like_df: pd.DataFrame, event_name: str, n: int = 0) -> int:
    """Return the event_id for the nth occurrence of the given event.

    Parameters
    ----------
    events_like_df : pd.DataFrame
        Events in the soccer game
    event_name : str
        Event name
    n : int, optional
        Nth occurence of the event in the game

    Returns
    -------
    int
        Event ID

    Raises
    ------
    ValueError
        Error when the dataframe doesnt have all the columns of Event dataset.
    """
    if not is_event_like_df(events_like_df):
        raise ValueError("Required a dataframe with all columns of Event")

    event_filter: pd.Series[bool] = events_like_df[Event.event] == event_name
    return events_like_df.loc[event_filter, Event.event_id].iloc[n]


def get_events_between(
    events_like_df: pd.DataFrame, event_id1: int, event_id2: int
) -> pd.DataFrame:
    """Return the set of events between the two given events.

    Parameters
    ----------
    events_like_df : pd.DataFrame
    event_id1 : int
    event_id2 : int

    Returns
    -------
    pd.DataFrame
        Events between the two given events

    Raises
    ------
    ValueError
        Error when the dataframe doesnt have all the columns of Event dataset.
    """
    if not is_event_like_df(events_like_df):
        raise ValueError("Required a dataframe with all columns of Event")

    event_id_col: str = Event.event_id
    filter_criteria: pd.Series = (events_like_df[event_id_col] > event_id1) & (
        events_like_df[event_id_col] < event_id2
    )

    return pd.DataFrame(events_like_df.loc[filter_criteria])
