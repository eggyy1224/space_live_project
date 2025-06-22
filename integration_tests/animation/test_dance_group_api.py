import requests
import json
import time

# Backend server URL
BASE_URL = "http://127.0.0.1:8000"
DANCE_GROUP_ENDPOINT = "/api/control/dance_group"
SEND_MESSAGE_ENDPOINT = "/api/control/send-message"

DANCE_URL = BASE_URL + DANCE_GROUP_ENDPOINT
MESSAGE_URL = BASE_URL + SEND_MESSAGE_ENDPOINT

def send_narration_message(message: str):
    """Sends a narration message to the frontend via the send-message endpoint."""
    headers = {"Content-Type": "application/json"}
    payload = {"content": message}
    print(f"\n--- Sending Narration ---")
    print(f"URL: {MESSAGE_URL}")
    print(f"Message: {message}")
    try:
        response = requests.post(MESSAGE_URL, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print("✅ Narration sent successfully.")
        else:
            print(f"❌ Failed to send narration. Status: {response.status_code}, Body: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred while sending narration: {e}")

def test_dance_group_control(formation, count, position, scale):
    """
    Tests the dance group control API endpoint by sending a POST request.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "formation": formation,
        "dancerCount": count,
        "position": position,
        "scale": scale
    }

    print(f"--- Testing Dance Group Control ---")
    print(f"URL: {DANCE_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(DANCE_URL, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            print(f"✅ Success! Status Code: {response.status_code}")
            print("Response Body:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Failure! Status Code: {response.status_code}")
            print("Response Body:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    SLEEP_DURATION = 8  # Seconds to wait between changes

    # Example 1: Change to a grid formation with 50 dancers
    test_dance_group_control(
        formation="grid",
        count=50,
        position=[0, -30, -40],
        scale=7.5
    )
    send_narration_message("為您呈現50人網格陣型")
    
    print(f"\n... Waiting for {SLEEP_DURATION} seconds ...")
    time.sleep(SLEEP_DURATION)
    print("\n" + "="*50 + "\n")

    # Example 2: Change to a line formation with 20 dancers
    test_dance_group_control(
        formation="line",
        count=20,
        position=[0, -10, 20],
        scale=10
    )
    send_narration_message("接下來是20人直線陣型")

    print(f"\n... Waiting for {SLEEP_DURATION} seconds ...")
    time.sleep(SLEEP_DURATION)
    print("\n" + "="*50 + "\n")

    # Example 3: Back to circle with 150 dancers
    test_dance_group_control(
        formation="circle",
        count=150,
        position=[0, -25, 0],
        scale=8
    )
    send_narration_message("最後變換為150人經典圓陣") 