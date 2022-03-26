import sys
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

from analysis.ball_tracker import compute_ball_trajectory_between_events
from analysis.pass_analyzer import PassingStatistics
from metadata import Event, EventType, TrackedPosition
from utils import event_utils


def load_csv_data(dataset_path: Path, column_dtypes: Mapping[str, np.dtype]) -> pd.DataFrame:
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
        f"initial kickoff to the first Ball Out of Play: {distance}"
    )

    passing_stats = PassingStatistics()
    # task-3
    passing_stats.add_pass_status(events_with_positions)
    player_with_most_passes: int = passing_stats.player_with_most_passes(events_with_positions)
    print(f"Player with most passes: {player_with_most_passes}")

    # task-4
    player_with_highest_completion_rate = passing_stats.player_with_max_pass_completion_rate(
        events_with_positions
    )
    print(f"Player with highest pass completion rate: {player_with_highest_completion_rate}")


def main(*args: str) -> None:
    data_dir: Path = Path(args[0]).absolute()
    events_csv: Path = data_dir / "events.csv"
    tracking_csv: Path = data_dir / "tracking.csv"

    events_df: pd.DataFrame = load_csv_data(events_csv, Event.column_types())
    event_utils.convert_event_time_to_ms(events_df)
    tracked_pos_df: pd.DataFrame = load_csv_data(tracking_csv, TrackedPosition.column_types())

    compute_challenges(events_df, tracked_pos_df)

    print("end")


if __name__ == "__main__":
    main(*sys.argv[1:])
