import sys
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd
from pandas.api.types import pandas_dtype

from ball_tracker import compute_ball_trajectory, get_event_id_for, get_events_between
from metadata import Event, EventType, TrackedPosition
from pass_analyzer import PassingStatistics


def convert_time_to_ms(time_in_sec: float, start_time_in_ms: int) -> int:
    return int(time_in_sec * 1000) - start_time_in_ms


def get_event_player_position(
    events: pd.DataFrame, positions: pd.DataFrame
) -> pd.DataFrame:

    time_col: str = Event.time
    start_time_in_ms: int = convert_time_to_ms(events[time_col].min(), 0)
    frame_number: str = "frame_number"

    events[time_col] = (
        events[time_col]
        .apply(convert_time_to_ms, start_time_in_ms=start_time_in_ms)
        .astype(pandas_dtype("Int64"))
    )

    # Pick the time frame that is closest to the event.
    events[frame_number] = (
        events[time_col].apply(lambda t: np.round(t / 40)).astype(pandas_dtype("Int64"))
    )

    positions[frame_number] = (
        positions[time_col].apply(lambda t: t // 40).astype(pandas_dtype("Int64"))
    )

    event_positions_df = events.merge(
        positions,
        how="left",
        on=[frame_number, Event.player_id],
        suffixes=(None, "_r"),
        validate="m:1",
    ).filter(Event.columns() + [TrackedPosition.x, TrackedPosition.y])

    events.drop(frame_number, axis=1, inplace=True)
    positions.drop(frame_number, axis=1, inplace=True)

    return event_positions_df


def load_csv_data(
    dataset_path: Path, column_dtypes: Mapping[str, np.dtype]
) -> pd.DataFrame:
    return pd.read_csv(
        dataset_path,
        sep=",",
        skiprows=[0],
        skip_blank_lines=True,
        names=column_dtypes.keys(),
        dtype=column_dtypes,
    )


def compute_challenges(events_df: pd.DataFrame, tracked_pos_df: pd.DataFrame) -> None:
    # task-1
    events_with_positions: pd.DataFrame = get_event_player_position(
        events_df, tracked_pos_df
    )

    # task-2
    init_kick_off_event: int = get_event_id_for(
        events_df, event_name=EventType.KICK_OFF, n=0
    )
    out_of_play_event: int = get_event_id_for(
        events_df, event_name=EventType.BALL_OUT_OF_PLAY, n=0
    )

    distance = compute_ball_trajectory(
        get_events_between(
            events_with_positions, init_kick_off_event, out_of_play_event
        )
    )
    print(
        "Length of the ball trajectory from the"
        f"initial kickoff to the first Ball Out of Play: {distance}"
    )

    passing_stats = PassingStatistics()
    # task-3
    passing_stats.add_pass_status(events_with_positions)
    player_with_most_passes: int = passing_stats.player_with_most_passes(
        events_with_positions
    )
    print(player_with_most_passes)

    # task-4
    player_with_highest_completion_rate = (
        passing_stats.player_with_max_pass_completion_rate(events_with_positions)
    )
    print(player_with_highest_completion_rate)


def main(*args: str) -> None:
    data_dir: Path = Path(args[0]).absolute()
    events_csv: Path = data_dir / "events.csv"
    tracking_csv: Path = data_dir / "tracking.csv"

    events_df: pd.DataFrame = load_csv_data(events_csv, Event.column_types())
    tracked_pos_df: pd.DataFrame = load_csv_data(
        tracking_csv, TrackedPosition.column_types()
    )

    compute_challenges(events_df, tracked_pos_df)

    print("end")


if __name__ == "__main__":
    main(*sys.argv[1:])
