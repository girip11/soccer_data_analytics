from contextlib import suppress

from pandas.api.types import pandas_dtype

from src.metadata import Metadata


def test_metadata() -> None:
    test_fields = {"event": pandas_dtype("str"), "event_id": pandas_dtype("Int64")}
    test_data = Metadata(test_fields)

    assert test_data.event == "event"
    assert test_data.event_id == "event_id"
    assert len(test_data.columns()) == 2

    assert test_data.column_types() == test_fields

    with suppress(AttributeError):
        test_data.event_name
