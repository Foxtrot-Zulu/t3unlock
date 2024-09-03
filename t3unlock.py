import usb.core
import usb.util
import struct
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants for USB device
VENDOR_ID = 0x04e8
PRODUCT_ID = 0x61f4
ENDPOINT_WRITE_TO_DEVICE = 0x02
ENDPOINT_READ_FROM_DEVICE = 0x81

# Constants for Payload Headers
HEADER_MAGIC_NUMBER = 0x55534243  # 'USBC' in hex
PAYLOAD_HEADER_LENGTH = 30

# Error codes and other constants
PAYLOAD_PARAM_1 = -42
PAYLOAD_PARAM_2 = -58
RELINK_COMMAND_PARAM = -24

def get_payload_header(param, payload_size):
    return struct.pack(
        '<4sI6xIBB2xBHBH', 
        HEADER_MAGIC_NUMBER.to_bytes(4, 'little'),  # 'USBC'
        10,  # Constant
        2,  # Another constant
        16, -123,  # More constants
        payload_size // 512,
        param,
        79,  # More constants
        194, 176  # More constants
    )


def get_password_payload(password):
    return get_byte_array(password.encode('utf-8'), 512)


def get_byte_array(input_bytes, length):
    return input_bytes.ljust(length, b'\x00')


def get_relink_command():
    return struct.pack(
        '<4sI6xIBB2xBHBH', 
        HEADER_MAGIC_NUMBER.to_bytes(4, 'little'),  # 'USBC'
        11,  # Constant
        0,  # Another constant
        6, -24,  # More constants
        0,
        0,  # Padding or unused values
        0, 0  # More padding
    )


class UsbHelper:
    def __init__(self, vendor_id, product_id, interface_number=0):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.interface_number = interface_number
        self.device = None

    def open(self, reset_device=False):
        self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
        if self.device is None:
            raise ValueError('Device not found')
        
        if reset_device:
            logging.info("Resetting device")
            self.device.reset()
        
        self.device.set_configuration()
        usb.util.claim_interface(self.device, self.interface_number)
        logging.info("Device opened and interface claimed")
    
    def bulk_transfer_write_to_device(self, endpoint, data):
        logging.info(f'Host->Device (length={len(data)}, endpoint={endpoint}): {list(data)}')
        transferred = self.device.write(endpoint, data, self.interface_number, timeout=5000)
        logging.info(f'{transferred} bytes sent')
    
    def bulk_transfer_read_from_device(self, endpoint, size):
        data = self.device.read(endpoint, size, self.interface_number, timeout=5000)
        logging.info(f'Device->Host: {list(data)}')
        logging.info(f'{len(data)} bytes read from device')
        return data

    def close(self):
        usb.util.release_interface(self.device, self.interface_number)
        usb.util.dispose_resources(self.device)
        self.device = None
        logging.info("Device closed and resources released")


def main(password):
    password_payload = get_password_payload(password)
    password_payload_header1 = get_payload_header(PAYLOAD_PARAM_1, len(password_payload))
    password_payload_header2 = get_payload_header(PAYLOAD_PARAM_2, len(password_payload))
    relink_command = get_relink_command()

    helper = UsbHelper(VENDOR_ID, PRODUCT_ID)
    try:
        helper.open(True)
        helper.bulk_transfer_write_to_device(ENDPOINT_WRITE_TO_DEVICE, password_payload_header1)
        helper.bulk_transfer_write_to_device(ENDPOINT_WRITE_TO_DEVICE, password_payload)
        helper.bulk_transfer_read_from_device(ENDPOINT_READ_FROM_DEVICE, 512)
        helper.bulk_transfer_write_to_device(ENDPOINT_WRITE_TO_DEVICE, password_payload_header2)
        helper.bulk_transfer_write_to_device(ENDPOINT_WRITE_TO_DEVICE, password_payload)
        helper.bulk_transfer_read_from_device(ENDPOINT_READ_FROM_DEVICE, 512)
        helper.bulk_transfer_write_to_device(ENDPOINT_WRITE_TO_DEVICE, relink_command)
        helper.bulk_transfer_read_from_device(ENDPOINT_READ_FROM_DEVICE, 512)
    except Exception as e:
        logging.error(f'Error: {e}')
    finally:
        helper.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python t3unlock.py <password>")
        sys.exit(1)
    main(sys.argv[1])
