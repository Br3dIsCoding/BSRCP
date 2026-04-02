import rotatescreen
import os
# Optional: Log when the script runs (useful for debugging)
def log_message(msg):
    # You can create a log file in your Streamer.bot directory
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screen_flip_log.txt")
    with open(log_path, "a") as f:
        f.write(f"{msg}\n")

def flip_screen():
    """Flip screen upside down or back to normal"""
    try:
        screen = rotatescreen.get_primary_display()
        
        if screen.current_orientation == 0:  # Currently landscape (normal)
            screen.set_landscape_flipped()    # Flip upside down
            print("SCREEN_FLIPPED")  # This goes to Streamer.bot's output
            log_message("Screen flipped upside down")
        else:  # Currently flipped
            screen.set_landscape()             # Back to normal
            print("SCREEN_NORMAL")
            log_message("Screen back to normal")
            
        # Always output something so Streamer.bot gets a response
        return True
    except Exception as e:
        print(f"ERROR: {str(e)}")
        log_message(f"Error: {str(e)}")
        return False

import websocket
import json
import uuid

import websocket
import json
import uuid
import time

def set_vtube_rotation(rotation_value):
    try:
        ws = websocket.create_connection("ws://127.0.0.1:8001")

        # Request token
        auth_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": str(uuid.uuid4()),
            "messageType": "AuthenticationTokenRequest",
            "data": {
                "pluginName": "Python Flip Controller",
                "pluginDeveloper": "bread"
            }
        }

        ws.send(json.dumps(auth_request))
        token = json.loads(ws.recv())["data"]["authenticationToken"]

        # Authenticate
        auth_confirm = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": str(uuid.uuid4()),
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": "Python Flip Controller",
                "pluginDeveloper": "bread",
                "authenticationToken": token
            }
        }

        ws.send(json.dumps(auth_confirm))
        ws.recv()

        # Set rotation
        rotate_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": str(uuid.uuid4()),
            "messageType": "MoveModelRequest",
            "data": {
                "timeInSeconds": 0.2,
                "valuesAreRelativeToModel": False,
                "rotation": rotation_value
            }
        }

        ws.send(json.dumps(rotate_request))
        ws.recv()

        ws.close()

    except Exception as e:
        print("VTS ERROR:", e)


if __name__ == "__main__":
    # You can accept arguments from Streamer.bot if needed
    # sys.argv contains any arguments passed
    flip_screen()
    set_vtube_rotation(180)
    time.sleep(120) #going to wait 2 minutes
    flip_screen() #flips the screen back
    set_vtube_rotation(0) # resets the vtuber model back