from time import sleep
import hid
import os
import ntcore

gamepad = hid.device()
gamepad.open(0x0079, 0x0011) # The vendor and product IDs of the gamepad
gamepad.set_nonblocking(True)

print(f"Opened gamepad: {gamepad['product_string']}")

if not os.path.exists("bit_names.txt"):
    print("Please create a file called bit_names.txt that maps the HID device's bit numbers to names.")
    print("There's a Jupyter notebook called interface.ipynb that can generate this by prompting you whenever a button is pressed.")
    exit()

BIT_NAMES = {}
with open("bit_names.txt", "r") as f:
    for line in f:
        bit, name = line.strip().split(" ", 1)
        BIT_NAMES[int(bit)] = name

print(f"Loaded {len(BIT_NAMES)} bit names: {BIT_NAMES}")


nt_instance = ntcore.NetworkTableInstance.getDefault()

print(f"Setting up NetworkTables client")
nt_instance.startClient4("NTControls")
nt_instance.setServer("127.0.0.1")
nt_instance.startDSClient()

# Wait for connection
print("Waiting for connection to NetworkTables server...")
while not nt_instance.isConnected():
    sleep(0.1)

print("Connected!")

controller_name = "Default"
# We use a table under SmartDashboard/ because AdvantageKit's LoggedDashboardValue can only use keys under SmartDashboard/
table = nt_instance.getTable("SmartDashboard/NTControls/" + controller_name)

BUTTON_TO_NT_INPUT = {
    # Manually authored for now
    "Up arrow": "LEFT_Y_POS",
    "Right arrow": "LEFT_Y_NEG",
    "Left arrow": "LEFT_X_NEG",
    "Down arrow": "LEFT_X_POS",
    "Start": "RIGHT_X_NEG",
    "Select": "RIGHT_X_POS",
    "Center": None, # N/A
    "Top right circle": ["LEFT_Y_POS", "LEFT_X_POS"],
    "Top left X": ["LEFT_Y_POS", "LEFT_X_NEG"],
    "Bottom left triangle": ["LEFT_Y_NEG", "LEFT_X_NEG"],
    "Bottom right square": ["LEFT_Y_NEG", "LEFT_X_POS"]
}

pressed_buttons = {}

while True:
    report = gamepad.read(64)
    if report:
        # Send every held button with its name to NetworkTables
        for bit, name in BIT_NAMES.items():
            if not name in BUTTON_TO_NT_INPUT or BUTTON_TO_NT_INPUT[name] == None:
                continue

            buttons = BUTTON_TO_NT_INPUT[name]
            if not isinstance(buttons, list):
                buttons = [buttons]
            
            pressed = report[bit // 8] & (1 << (bit % 8))
            for button in buttons:
                if not button in pressed_buttons:
                    pressed_buttons[button] = set()
                
                prev_pressed = len(pressed_buttons[button]) > 0
                if pressed:
                    pressed_buttons[button].add(name)
                else:
                    pressed_buttons[button].discard(name)
                new_pressed = len(pressed_buttons[button]) > 0

                if prev_pressed != new_pressed:
                    print(f"Sending {button} {new_pressed}")
                    table.putBoolean(button, new_pressed)
                
        sleep(1.0 / 60)
    else:
        print("No data...")
        sleep(0.1)