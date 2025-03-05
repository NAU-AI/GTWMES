from dataclasses import dataclass


@dataclass
class CounterRecordDTO:
    output_code: str
    value: int
