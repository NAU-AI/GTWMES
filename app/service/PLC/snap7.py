import snap7

# Set the PLC IP, rack, and slot here
plc_ip = "192.168.1.10"
rack = 0
slot = 1

def plc_connect():
    try:
        # Create a Snap7 client instance
        plc = snap7.client.Client()
        # Attempt to connect to the PLC using the configured parameters
        plc.connect(plc_ip, rack, slot)
        print(f"Connected to PLC at {plc_ip}")
        return plc  # Return the connected PLC instance
    except: #snap7.exceptions.Snap7Exception as e:
        # Handle exceptions if there's an issue with the PLC connection
        print(f"Error connecting to PLC")
        return None

def plc_disconnect(plc):
    try:
        # Disconnect from the PLC
        plc.disconnect()
        print(f"Disconnected to PLC at {plc_ip}")
    except: #snap7.exceptions.Snap7Exception as e:
        # Handle exceptions if there's an issue with the PLC connection
        print(f"Error disconnecting from PLC")

from snap7 import type


def read_multiple_variables(plc, items):
    """
    Read multiple variables in a single request.

    Args:
    - plc: Snap7 client instance.
    - items: List of items to read. Each item is a tuple (area, start, size, datatype).
      Example: [(23, 0, 3, snap7.type.S7WLInt), (4, 0, 66, snap7.type.S7WLInt)]

    Returns:
    - List of values corresponding to the read items.
    """
    # Create a list of ctype objects for each item
    ctype_items = [type.S7DataItem() for _ in items]

    # Populate the ctype objects with item information
    for i, (area, start, size) in enumerate(items):
        ctype_items[i].Area = area  # No need to encode to bytes
        #ctype_items[i].WordLen = datatype
        ctype_items[i].Result = 0  # Initialize the Result field
        ctype_items[i].DBNumber = start
        ctype_items[i].Start = start
        ctype_items[i].Amount = size

    # Convert the list of ctype objects to a ctype array
    ctype_array = (type.S7DataItem * len(ctype_items))(*ctype_items)

    # Perform the read operation
    result = plc.read_multi_vars(ctype_array)

    # Check if the result is an integer (indicating an error code)
    if isinstance(result, int):
        raise ValueError(f"Read operation failed with error code: {result}")

    # Extract values from the result
    values = [item.Data for item in result]

    return values


def read_bool(plc, db_number, byte_offset, bit_offset):
    try:
        # Read a single Boolean (bit) from the specified DB, byte, and bit offset
        data = plc.read_area(snap7.type.Areas.DB, db_number, byte_offset, 1)  # Read 1 byte

        # Extract the Boolean value from the specified bit
        bool_value = bool(data[0] & (1 << bit_offset))

        return bool_value

    except Exception as e:
        # Handle exceptions if there's an issue with the PLC connection
        print(f"Error reading Boolean")
        raise Exception("Error reading Boolean")

def write_bool(plc, db_number, byte_offset, bit_offset, value):
    try:
        # Read the current byte from the specified DB and byte offset
        data = plc.read_area(snap7.type.Areas.DB, db_number, byte_offset, 1)

        # Modify the specific bit in the byte based on the 'value' argument
        if value:
            # Set the bit to 1
            data[0] |= 1 << bit_offset
        else:
            # Set the bit to 0
            data[0] &= ~(1 << bit_offset)

        # Write the modified byte back to the PLC
        plc.write_area(snap7.type.Areas.DB, db_number, byte_offset, data)

    except snap7.exceptions.Snap7Exception as e:
        # Handle exceptions if there's an issue with the PLC connection
        print(f"Error writing Boolean: {e}")

def read_int(plc, db_number, byte_offset):
    try:
        # Read a 16-bit integer (2 bytes) from the specified DB and byte offset
        data = plc.read_area(snap7.type.Areas.DB, db_number, byte_offset, 2)  # Read 2 bytes

        # Convert the two bytes to a 16-bit integer (big-endian)
        int_value = snap7.util.get_int(data, 0)

        return int_value

    except Exception as e:
        # Handle exceptions if there's an issue with the PLC connection
        print(f"Error reading integer")
        raise Exception("Error reading integer")

def read_uint(plc, db_number, byte_offset):
    try:
        # Read a 16-bit integer (2 bytes) from the specified DB and byte offset
        data = plc.read_area(snap7.type.Areas.DB, db_number, byte_offset, 2)  # Read 2 bytes

        # Convert the two bytes to a 16-bit integer (big-endian)
        uint_value = snap7.util.get_uint(data, 0)

        return uint_value

    except Exception as e:
        # Handle exceptions if there's an issue with the PLC connection
        print(f"Error reading uinteger")
        raise Exception("Error reading uinteger")

def write_int(plc, db_number, byte_offset, value):
    try:
        # Convert the integer value to a 16-bit binary representation
        data = bytearray([0, 0])  # Create a 2-byte bytearray with initial values

        # Set the integer value in the bytearray at the correct offset (big-endian)
        data[0] = (value >> 8) & 0xFF  # Most significant byte
        data[1] = value & 0xFF         # Least significant byte

        # Write the 16-bit integer (2 bytes) to the specified DB and byte offset
        plc.write_area(snap7.type.Areas.DB, db_number, byte_offset, data)

    except snap7.exceptions.Snap7Exception as e:
        # Handle exceptions if there's an issue with the PLC connection
        print(f"Error writing integer: {e}")


def read_real(plc, db_number, byte_offset):
    try:
        # Read a 32-bit floating-point value (4 bytes) from the specified DB and byte offset
        data = plc.read_area(snap7.type.Areas.DB, db_number, byte_offset, 4)  # Read 4 bytes

        # Convert the four bytes to a 32-bit floating-point value (big-endian)
        real_value = snap7.util.get_real(data, 0)

        return real_value

    except snap7.exceptions.Snap7Exception as e:
        # Handle exceptions if there's an issue with the PLC connection
        print(f"Error reading real value: {e}")
        return None

def write_real(plc, db_number, byte_offset, value):
    try:
        # Convert the real value to a 32-bit binary representation
        data = bytearray([0, 0, 0, 0])  # Create a 4-byte bytearray with initial values

        # Set the real value in the bytearray at the correct offset (big-endian)
        snap7.util.set_real(data, 0, value)

        # Write the 32-bit floating-point value (4 bytes) to the specified DB and byte offset
        plc.write_area(snap7.type.Areas.DB, db_number, byte_offset, data)

    except snap7.exceptions.Snap7Exception as e:
        # Handle exceptions if there's an issue with the PLC connection
        print(f"Error writing real value: {e}")






