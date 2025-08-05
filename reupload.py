import json
import time
import requests
import os

FAILED_POLLS_FILE = "failed_polls.json" # enter the path to your JSON with failed polls
OUTPUT_FILE = "retried_assets.json" # omitting the path will save the files to your user folder
STILL_FAILED_FILE = "still_failed.json"

HEADERS = {
    "x-api-key": "your-key-here",  # Replace this with your Roblox Open Cloud API key
    "Content-Type": "application/json"
}

def poll_operation(operation_url, asset_name, max_retries=5):
    retry_delay = 3  # seconds
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(operation_url, headers=HEADERS)
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get("done", False):
                    asset_id = json_data.get("response", {}).get("assetId")
                    if asset_id:
                        print(f"[SUCCESS] {asset_name} => {asset_id}")
                        return asset_id
                    else:
                        print(f"[ERROR] No asset ID for {asset_name}")
                        return None
                else:
                    print(f"[WAIT] Not done yet ({asset_name}) - Attempt {attempt}")
            else:
                print(f"[HTTP ERROR] {asset_name} => {response.status_code} {response.text}")
        except Exception as e:
            print(f"[EXCEPTION] {asset_name} => {e}")

        time.sleep(retry_delay)
        retry_delay *= 2  # exponential backoff

    print(f"[FAILED] Max retries reached for {asset_name}")
    return None

def retry_failed_polls():
    if not os.path.exists(FAILED_POLLS_FILE):
        print(f"[ERROR] File not found: {FAILED_POLLS_FILE}")
        return

    with open(FAILED_POLLS_FILE, "r") as f:
        failed_polls = json.load(f)

    results = {}
    still_failed = []

    for entry in failed_polls:
        name = entry["name"]
        url = entry["operation_url"]
        asset_id = poll_operation(url, name)
        if asset_id:
            results[name] = asset_id
        else:
            still_failed.append(entry)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=4)
    print(f"[SAVED] Successful IDs to {OUTPUT_FILE}")

    if still_failed:
        with open(STILL_FAILED_FILE, "w") as f:
            json.dump(still_failed, f, indent=4)
        print(f"[WARNING] {len(still_failed)} operations still failed — saved to {STILL_FAILED_FILE}")
    else:
        print("[DONE] All previously failed polls succeeded!")

if __name__ == "__main__":
    retry_failed_polls()
