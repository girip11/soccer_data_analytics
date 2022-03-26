import numpy as np

from src.metadata import Event, EventType
from src.utils import event_utils
from tests.utils import get_event_df, get_test_events


def test_convert_time_to_ms() -> None:
    events_df = get_event_df(
        [
            [0, 1, 625.68, 358112, 1935290, "Kick Off"],
            [1, 1, 625.68, 358112, 1935290, "Pass"],
            [2, 1, 626.69, 339987, 1935290, "Reception"],
        ]
    )
    event_utils.convert_event_time_to_ms(events_df)

    assert events_df.iloc[0][Event.time] == 0
    assert events_df.iloc[1][Event.time] == 0
    assert events_df.iloc[2][Event.time] == 1010


def test_get_event_id() -> None:
    test_events_df = get_test_events()
    assert event_utils.get_event_id_for(test_events_df, EventType.KICK_OFF, 0) == 0
    assert event_utils.get_event_id_for(test_events_df, EventType.BALL_OUT_OF_PLAY, 0) == 10


def test_get_events_between() -> None:
    test_events_df = get_test_events()
    event1: int = event_utils.get_event_id_for(test_events_df, EventType.KICK_OFF, 0)
    event2: int = event_utils.get_event_id_for(test_events_df, EventType.BALL_OUT_OF_PLAY, 0)

    subevents = event_utils.get_events_between(test_events_df, event1, event2)

    assert len(subevents) == (event2 - event1) - 1
    assert subevents.iloc[0][Event.event_id] == event1 + 1
    assert subevents.iloc[-1][Event.event_id] == event2 - 1


def test_is_event_like_df() -> None:
    test_events_df = get_test_events()
    assert event_utils.is_event_like_df(test_events_df)

    test_events_df = test_events_df.assign(pass_status=np.full(test_events_df.shape[0], -1))
    assert event_utils.is_event_like_df(test_events_df)

    test_events_df.drop(Event.event, inplace=True, axis=1)
    assert not event_utils.is_event_like_df(test_events_df)
