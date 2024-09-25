from service.PLC.snap7 import plc_connect, plc_disconnect, read_int 
import snap7

def main():
    # Connect to the PLC
    plc = plc_connect()
    
    if plc is None:
        print("Failed to connect to PLC.")
        return

    
    # DB number where the variables are located
    db_number = 8

    # Read variables from DB8
    equipment_status = read_int(plc, 8, 4)
    active_time = read_int(plc, db_number, 6)
    alarm0 = read_int(plc, db_number, 8)
    alarm1 = read_int(plc, db_number, 10)
    alarm2 = read_int(plc, db_number, 12)
    alarm3 = read_int(plc, db_number, 14)
    output0 = read_int(plc, db_number, 16)
    output1 = read_int(plc, db_number, 18)

    # Print the results
    print(f"Equipment Status (Int): {equipment_status}")
    print(f"Active Time (Int): {active_time}")
    print(f"Alarm 0 (Int): {alarm0}")
    print(f"Alarm 1 (Int): {alarm1}")
    print(f"Alarm 2 (Int): {alarm2}")
    print(f"Alarm 3 (Int): {alarm3}")
    print(f"Output 0 (Int): {output0}")
    print(f"Output 1 (Int): {output1}")


    # Disconnect from the PLC
    plc_disconnect(plc)

if __name__ == "__main__":
    main()
