from snap7 import types, util

TYPE_SPECS = {
    "bool": {
        "amount": 1,
        "wordlen": types.S7WLByte,
        "convert": lambda data, item: bool(data[0] & (1 << item.get("bit", 0)))
    },
    "int": {
        "amount": 2,
        "wordlen": types.S7WLWord,
        "convert": lambda data, item: util.get_int(data, 0)
    },
    "real": {
        "amount": 4,
        "wordlen": types.S7WLReal,
        "convert": lambda data, item: util.get_real(data, 0)
    }
}
