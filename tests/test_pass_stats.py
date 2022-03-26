from typing import Any, List

import pytest

from src.analysis.pass_statistics import (
    PASS_STATUS_COL,
    compute_pass_status,
    is_long_pass_completed,
    is_short_pass_completed,
)
from tests.utils import get_event_df, get_test_events


@pytest.mark.parametrize(
    "events, expected",
    (
        (
            [[1, 1, 625.68, 358112, 1935290, "Pass"], [2, 1, 626.69, 339987, 1935290, "Reception"]],
            True,
        ),
        (
            [[1, 1, 625.68, 358112, 1935290, "Pass"], [2, 1, 626.69, 339987, 1935290, "Pass"]],
            True,
        ),
        (
            [
                [1, 1, 625.68, 358112, 1935290, "Pass"],
                [2, 1, 626.69, 339987, 1935290, "Interception"],
            ],
            False,
        ),
        (
            [
                [1, 1, 625.68, 358112, 1935290, "Cross"],
                [2, 1, 626.69, 339987, 1935290, "Clearance"],
            ],
            False,
        ),
        (
            [
                [1, 1, 625.68, 358112, 1935290, "Cross"],
                [2, 1, 626.69, 339987, 1935290, "Interception"],
            ],
            False,
        ),
    ),
)
def test_short_pass_completion(events: List[List[Any]], expected: bool) -> None:
    events_df = get_event_df(events)
    assert expected == is_short_pass_completed(events_df)


@pytest.mark.parametrize(
    "events, expected",
    (
        (
            [
                [1, 1, 625.68, 358112, 1935290, "Pass"],
                [2, 1, 626.69, 123456, 1935226, "Clearance"],
                [3, 1, 627.69, 339987, 1935290, "Reception"],
            ],
            True,
        ),
        (
            [
                [1, 1, 625.68, 358112, 1935290, "Pass"],
                [2, 1, 626.69, 123456, 1935226, "Clearance"],
                [2, 1, 627.69, 339987, 1935226, "Interception"],
            ],
            False,
        ),
        (
            [
                [1, 1, 625.68, 358112, 1935290, "Cross"],
                [2, 1, 626.69, 123456, 1935226, "Clearance"],
                [3, 1, 627.69, 339987, 1935290, "Reception"],
            ],
            True,
        ),
        (
            [
                [1, 1, 625.68, 358112, 1935290, "Cross"],
                [2, 1, 626.69, 123456, 1935226, "Defensive Event"],
                [2, 1, 627.69, 339987, 1935226, "Interception"],
            ],
            False,
        ),
    ),
)
def test_long_pass_completion(events: List[List[Any]], expected: bool) -> None:
    events_df = get_event_df(events)
    assert expected == is_long_pass_completed(events_df)


def test_compute_pass_status() -> None:
    events_df = get_test_events()
    events_df = compute_pass_status(events_df)

    def get_pass_status(event_id: int) -> int:
        return events_df.loc[events_df.event_id == event_id, PASS_STATUS_COL].iloc[0]

    assert get_pass_status(1) == 1
    assert get_pass_status(3) == 1
    assert get_pass_status(6) == 0
    assert get_pass_status(8) == 0
    assert get_pass_status(7) == -1
    assert get_pass_status(9) == -1
