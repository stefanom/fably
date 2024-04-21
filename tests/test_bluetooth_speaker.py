import bluetooth

def find_bluetooth_speakers():
    print("Searching for devices...")
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)
    speakers = [device for device in nearby_devices if 'Speaker' in device[1]]
    return speakers

def connect_to_speaker(device_address):
    # Establishing a connection to the Bluetooth device
    # Note: Actual connection methods may vary based on the device and profiles supported.
    # This example assumes a serial port profile.
    service_matches = bluetooth.find_service(address=device_address)

    if len(service_matches) == 0:
        print("Couldn't find the device's service.")
        return False

    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    print(f"Connecting to \"{name}\" on {host}")

    # Create the client socket and connect to it
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        sock.connect((host, port))
        print("Connected successfully.")
        return sock
    except bluetooth.btcommon.BluetoothError as err:
        print(f"Failed to connect: {err}")
        return False

def main():
    speakers = find_bluetooth_speakers()
    if speakers:
        print(f"Found {len(speakers)} speakers.")
        for addr, name in speakers:
            print(f"Trying to connect to {name} at {addr}")
            sock = connect_to_speaker(addr)
            if sock:
                # You can add further interaction with the speaker here
                sock.close()  # Make sure to close the socket when done
                break
    else:
        print("No Bluetooth speakers found.")

if __name__ == "__main__":
    main()
