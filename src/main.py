import os
import sys
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

from src.analysis.ball_tracker import compute_ball_trajectory_between_events
from src.analysis.pass_statistics import (
    compute_pass_status,
    find_most_pass_completing_player,
    find_most_passing_player,
)
from src.metadata import Event, EventType, TrackedPosition
from src.utils import event_utils


def load_csv_data(dataset_path: Path, column_dtypes: Mapping[str, np.dtype]) -> pd.DataFrame:
    """Return the dataframe from CSV file

    Parameters
    ----------
    dataset_path : Path
        Path to the csv file
    column_dtypes : Mapping[str, np.dtype]
        column names and type metadata

    Returns
    -------
    pd.DataFrame
    """
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
    events_with_positions: pd.DataFrame = event_utils.add_position_to_event(
        events_df, tracked_pos_df
    )

    # task-2
    distance = compute_ball_trajectory_between_events(
        events_with_positions, (EventType.KICK_OFF, 0), (EventType.BALL_OUT_OF_PLAY, 0)
    )
    print(
        "Length of the ball trajectory from the "
        f"initial kickoff to the first Ball Out of Play: {distance} meters"
    )

    # task-3
    events_with_pass_status: pd.DataFrame = compute_pass_status(events_with_positions)
    player_id, passes = find_most_passing_player(events_with_pass_status)
    print(f"Player {player_id} made most passes with count {passes} ")

    # task-4
    player_id, completion_rate, total_passes = find_most_pass_completing_player(
        events_with_pass_status
    )
    print(
        f"Player {player_id} has the best pass completion rate of {completion_rate}% "
        f"with {total_passes} passes"
    )


def main(*args: str) -> None:
    data_dir: Path = Path(args[0] if len(args) == 1 else os.environ["DATA_DIR"]).absolute()
    events_csv: Path = data_dir / "events.csv"
    tracking_csv: Path = data_dir / "tracking.csv"

    events_df: pd.DataFrame = load_csv_data(events_csv, Event.column_types())
    event_utils.convert_event_time_to_ms(events_df)
    tracked_pos_df: pd.DataFrame = load_csv_data(tracking_csv, TrackedPosition.column_types())

    print("Performing analysis on the data...")
    compute_challenges(events_df, tracked_pos_df)
    print("Completed the analysis.")


if __name__ == "__main__":
    main(*sys.argv[1:])
