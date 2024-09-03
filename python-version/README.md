# This utility is provided as-is, use it at your own risk. I cannot be held responsible for any damage to any of your devices due to the use of this utility.


## This is a Python rewrite of the orginal t3unlock in Java by: https://github.com/rsenden

t3unlock 

This is a simple Python utility for unlocking (logging in to) a Samsung portable SSD T3 drive on any platform that has a libusb implementation. Since Samsung doesn't provide a utility for logging in to the drive under Linux, this utility was specifically developed for use under Linux.

1. Install pyusb Library:
* Before running the code, you need to install the pyusb library. You can do this using pip:
```shell
          sh
          Copy code
          pip install pyusb
```

    2. Connect the USB Device:
        ◦ Make sure the USB device with vendorId = 0x04e8 and productId = 0x61f4 is connected to your system.
    3. Run the Python Script:
        ◦ Save the above Python code to a file named t3unlock.py.
        ◦ Open a terminal or command prompt, navigate to the directory where the script is saved, and run the script with the password as an argument:
          sh
          Copy code
          python t3unlock.py <password>
        ◦ Replace <password> with the actual password you want to use.
    4. Permissions:
        ◦ On Linux, you might need to run the script with elevated permissions (using sudo) if your user doesn't have the necessary permissions to interact with USB devices:
          sh
          Copy code
          sudo python t3unlock.py <password>
Notes:
    • Device Specifics: Ensure that your USB device matches the vendorId and productId specified in the code. If not, you will need to adjust these values to match your device.
    • Testing Environment: This code is designed to run in a Python environment with access to the USB device. It assumes that the USB device is configured correctly and that pyusb can communicate with it.

Improvements besides rewrite:

Constants for Magic Numbers:
Replaced magic numbers with named constants, better readability and maintenance.
Added HEADER_MAGIC_NUMBER, PAYLOAD_HEADER_LENGTH, and others for clarity.

Logging Framework:
Replaced print statements with Python’s logging module.
Logger displays messages with timestamp, log level, and message.

Structured Data Handling:
Used Python’s struct.pack with a more readable format string, grouping constants logically to represent the headers and commands.
to_bytes packs the header correctly according to the intended format.

Resource Management:
All USB resources are correctly released with the usb.util.dispose_resources method, which is explicitly logged.
