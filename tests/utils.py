from pathlib import Path
from typing import Any, List

import pandas as pd
from pandas.api.types import pandas_dtype

from src.metadata import Event


def get_event_df(rows: List[List[Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=Event.columns()).astype(Event.column_types())


def get_events_with_pos_df(rows: List[List[Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=Event.columns() + ["x", "y"]).astype(
        {
            **Event.column_types(),
            "x": pandas_dtype("Int16"),
            "y": pandas_dtype("Int16"),
        }
    )


def get_test_events() -> pd.DataFrame:
    return pd.read_csv(
        Path(__file__).parent / "test_data/events.csv",
        sep=",",
        skiprows=[0],
        skip_blank_lines=True,
        names=Event.columns(),
        dtype=Event.column_types(),
    )
