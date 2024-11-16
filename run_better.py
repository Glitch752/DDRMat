from time import sleep
from math import sqrt
import vgamepad as vg
import hid
import keyboard

gamepad = hid.device()
gamepad.open(0x0079, 0x0011) # The vendor and product IDs of the gamepad
gamepad.set_nonblocking(True)

print(gamepad)

virtualGamepad = vg.VX360Gamepad()

BIT_NAMES = {}

# Load the bit names from a file
with open("bit_names.txt", "r") as f:
    for line in f:
        bit, name = line.strip().split(" ", 1)
        BIT_NAMES[int(bit)] = name

print(f"Loaded {len(BIT_NAMES)} bit names: {BIT_NAMES}")

def is_pressed(name):
    bit = 0
    for bit_bit, bit_name in BIT_NAMES.items():
        if bit_name == name:
            bit = bit_bit
            break
    pressed = report[bit // 8] & (1 << (bit % 8))
    return pressed != 0

def reorient():
    print("Reorienting")
    virtualGamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
    virtualGamepad.update()
    sleep(0.2)
    virtualGamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
    virtualGamepad.update()

# reorient()
keyboard.add_hotkey('x', reorient, suppress=True)

horizontal_filter = []
vertical_filter = []
turn_filter = []
linear_filter_samples = 40

while True:
    report = gamepad.read(64)
    if report:
        horizontal = 0
        vertical = 0
        turn = 0
        if is_pressed("Up arrow"):
            vertical += 1
        if is_pressed("Down arrow"):
            vertical -= 1
        if is_pressed("Left arrow"):
            horizontal -= 1
        if is_pressed("Right arrow"):
            horizontal += 1
        
        if is_pressed("Top right circle"):
            vertical += 1
            horizontal += 1
        if is_pressed("Top left X"):
            vertical += 1
            horizontal -= 1
        if is_pressed("Bottom left triangle"):
            vertical -= 1
            horizontal -= 1
        if is_pressed("Bottom right square"):
            vertical -= 1
            horizontal += 1
        
        if is_pressed("Start"):
            turn += 0.5
        if is_pressed("Select"):
            turn -= 0.5
        
        drive_magnitude = 1.0
        current_drive_mag = sqrt(horizontal * horizontal + vertical * vertical)
        if current_drive_mag == 0:
            current_drive_mag = 1
        horizontal /= current_drive_mag / drive_magnitude
        vertical /= current_drive_mag / drive_magnitude

        horizontal_filter.append(horizontal)
        if len(horizontal_filter) > linear_filter_samples:
            horizontal_filter.pop(0)
        vertical_filter.append(vertical)
        if len(vertical_filter) > linear_filter_samples:
            vertical_filter.pop(0)
        turn_filter.append(turn)
        if len(turn_filter) > linear_filter_samples:
            turn_filter.pop(0)

        horizontal_average = sum(horizontal_filter) / len(horizontal_filter)
        vertical_average = sum(vertical_filter) / len(vertical_filter)
        turn_average = sum(turn_filter) / len(turn_filter)

        # if vertical != 0 or horizontal != 0:
        #     print(horizontal, vertical)

        virtualGamepad.left_joystick_float(horizontal_average, vertical_average)
        virtualGamepad.right_joystick_float(turn_average, 0)
        virtualGamepad.update()