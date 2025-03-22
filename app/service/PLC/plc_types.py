from snap7 import types, util


def convert_bool(data, item):
    if "bit" not in item:
        raise KeyError("Missing 'bit' field for boolean conversion")
    return bool(data[0] & (1 << item["bit"]))


TYPE_SPECS = {
    "BOOL": {
        "amount": 1,
        "wordlen": types.S7WLByte,
        "convert": convert_bool,
    },
    "INT": {
        "amount": 2,
        "wordlen": types.S7WLWord,
        "convert": lambda data, item: util.get_int(data, 0),
    },
    "UINT": {
        "amount": 2,
        "wordlen": types.S7WLWord,
        "convert": lambda data, item: util.get_uint(data, 0),
    },
    "REAL": {
        "amount": 4,
        "wordlen": types.S7WLReal,
        "convert": lambda data, item: util.get_real(data, 0),
    },
}
