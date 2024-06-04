import subprocess

def is_bluetooth_on():
    try:
        devices = subprocess.check_output(["bluetoothctl", "show"]).decode('utf-8').split('\n')
        for device in devices:
            if "Powered" in device:
                return "yes" in device
    except Exception as e:
        return False
    
def get_paired_devices():
    # "bluetoothctl devices | grep Device | cut -d ' ' -f 2"
    devices = subprocess.check_output(["bluetoothctl", "devices"]).decode('utf-8').split('\n')
    device_struct = []
    for device in devices:
        if "Device" in device:
            device_struct.append({
                "name": " ".join(device.split(" ")[2:]),
                "mac": device.split(" ")[1],
            })
    return device_struct

def connect_device(mac):
    return subprocess.check_output(["bluetoothctl", "connect", mac]).decode('utf-8')

def disconnect_device(mac):
    return subprocess.check_output(["bluetoothctl", "disconnect", mac]).decode('utf-8')

def get_connected_devices():
    try:
        devices = subprocess.check_output(["bluetoothctl", "info"]).decode('utf-8').split('\n')
        device_struct = []
        for device in devices:
            if "Device" in device:
                device_struct.append({
                    "mac": device.split(" ")[1],
                })
        return device_struct
    except Exception as e:
        return []
