from src.analysis.ball_tracker import compute_ball_trajectory_between_events
from src.metadata import EventType
from tests.utils import get_events_with_pos_df


def test_ball_trajectory_length() -> None:
    events_df = get_events_with_pos_df(
        [
            [0, 1, 625.68, 358112, 1935290, "Kick Off", 5250, 3400],
            [1, 1, 625.68, 358112, 1935290, "Pass", 5250, 3400],
            [2, 1, 626.69, 339987, 1935290, "Reception", 5500, 4000],
            [10, 1, 633.76, -1, -1, "Ball Out of Play", -1, -1],
        ]
    )

    assert (
        compute_ball_trajectory_between_events(
            events_df, (EventType.KICK_OFF, 0), (EventType.BALL_OUT_OF_PLAY, 0)
        )
        == 6.50
    )
