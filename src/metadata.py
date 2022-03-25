from typing import Dict, List, Mapping

import numpy as np
from pandas.api.types import pandas_dtype
from strenum import StrEnum


class Metadata:
    _fields: Dict[str, np.dtype]

    def __init__(self, fields: Mapping[str, np.dtype]) -> None:
        self._fields = {**fields}

    def columns(self) -> List[str]:
        return list(self._fields.keys())

    def column_types(self) -> Mapping[str, np.dtype]:
        return self._fields

    def __getattr__(self, col: str) -> str:
        if col in self._fields:
            return col

        raise AttributeError(f"Type Event has no attribute {col}")


Event: Metadata = Metadata(
    {
        "event_id": pandas_dtype("Int64"),
        "half_time": pandas_dtype("Int8"),
        "time": np.dtype(np.float64),
        "player_id": pandas_dtype("Int64"),
        "team_id": pandas_dtype("Int64"),
        "event": pandas_dtype("str"),
    }
)

TrackedPosition: Metadata = Metadata(
    {
        "half_time": pandas_dtype("Int8"),
        "time": pandas_dtype("Int64"),
        "player_id": pandas_dtype("Int64"),
        "team_id": pandas_dtype("Int64"),
        "x": pandas_dtype("Int16"),
        "y": pandas_dtype("Int16"),
    }
)

# Events can be converted to uniform case
class EventType(StrEnum):
    KICK_OFF = "Kick Off"
    PASS = "Pass"
    RECEPTION = "Reception"
    BALL_OUT_OF_PLAY = "Ball Out of Play"
    FREEKICK = "Freekick"
    CLEARANCE = "Clearance"
    CROSS = "Cross"
    DEFENSIVE_EVENT = "Defensive Event"
    BALL_PROGRESSION = "Ball Progression"
    INTERCEPTION = "Interception"
    GOALKICK = "Goalkick"
    ATTEMPT_AT_GOAL = "Attempt at Goal"
    CORNER = "Corner"
    THROW_IN = "Throw in"
