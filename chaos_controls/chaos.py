import threading
import time
import random
import keyboard
import pyautogui
import sys

# ===== STATE =====
effects = {
    "no_turn": False,
    "invert_mouse": False,
    "shuffle_keys": False,
    "chaos": False
}

key_map = {}
letters = ['w', 'a', 's', 'd']

# ===== WASD SHUFFLE =====
def activate_shuffle(duration=15):
    global key_map

    shuffled = letters[:]
    random.shuffle(shuffled)
    key_map = dict(zip(letters, shuffled))

    print("WASD SHUFFLED:", key_map)

    effects["shuffle_keys"] = True

    # Clear old hooks just in case
    keyboard.unhook_all()

    # Remap each key properly
    for key in letters:
        keyboard.add_hotkey(key, lambda k=key: remap_key(k), suppress=True)

    start = time.time()
    while time.time() - start < duration and running:
        time.sleep(0.1)

    # RESET
    keyboard.unhook_all()
    effects["shuffle_keys"] = False

    print("WASD RESET")


def remap_key(k):
    if effects["shuffle_keys"]:
        new_key = key_map[k]
        keyboard.press_and_release(new_key)
        print(f"{k} -> {new_key}")


# ===== NO TURNING =====
def lock_mouse():
    screen_w, screen_h = pyautogui.size()
    center_x, center_y = screen_w // 2, screen_h // 2

    while effects["no_turn"] and running:
        pyautogui.moveTo(center_x, center_y)
        time.sleep(0.01)


def activate_no_turn(duration=10):
    effects["no_turn"] = True
    print("NO TURNING ACTIVATED")

    threading.Thread(target=lock_mouse).start()

    start = time.time()
    while time.time() - start < duration and running:
        time.sleep(0.1)
    effects["no_turn"] = False
    print("NO TURNING OFF")


# ===== MOUSE INVERT (RELIABLE VERSION) =====
# ⚠️ Uses a keybind you set in your game (recommended)

def activate_invert(duration=10):
    print("MOUSE INVERT ACTIVATED")

    # 👉 CHANGE THIS to your in-game invert toggle key
    INVERT_KEY = "f9"

    keyboard.press_and_release(INVERT_KEY)  # turn ON
    start = time.time()
    while time.time() - start < duration and running:
        time.sleep(0.1)
    keyboard.press_and_release(INVERT_KEY)  # turn OFF

    print("MOUSE INVERT OFF")

# ===== CHAOS MODE =====
# Shuffle & No camera movement for 120 seconds (2 minutes)

def activate_chaos(duration=120):
    print("CHAOS HAS STARTED")
    effects["chaos"] = True
    activate_shuffle(duration)
    activate_no_turn(duration)
    start = time.time()
    while time.time() - start < duration and running:
        time.sleep(0.1)
    effects["chaos"] = False
    print("Chaos has been disabled")

running = False

def start_chaos(duration=120):
    global running
    running = True
    threading.Thread(target=activate_chaos, args=(duration,), daemon=True).start()


def start_shuffle(duration=15):
    global running
    running = True
    threading.Thread(target=activate_shuffle, args=(duration,), daemon=True).start()


def start_no_turn(duration=10):
    global running
    running = True
    threading.Thread(target=activate_no_turn, args=(duration,), daemon=True).start()


def start_invert(duration=10):
    global running
    running = True
    threading.Thread(target=activate_invert, args=(duration,), daemon=True).start()


def stop_chaos():
    global running
    running = False

    # Turn everything OFF
    effects["no_turn"] = False
    effects["shuffle_keys"] = False
    effects["chaos"] = False

    keyboard.unhook_all()
    print("CHAOS FORCE STOPPED")
# ===== TEST =====
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "no_turn":
            threading.Thread(target=activate_no_turn).start()

        elif cmd == "invert":
            threading.Thread(target=activate_invert).start()

        elif cmd == "shuffle":
            threading.Thread(target=activate_shuffle).start()

        elif cmd == "chaos":
            threading.Thread(target=activate_chaos).start()