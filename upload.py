import os
import requests
import json
from time import sleep

# Configuration
API_KEY = "your-key-here"
CREATOR_TYPE = "group"  # group or user
CREATOR_ID = "your-id-here"
UPLOAD_FOLDER = r"path-to-your-folder"
ASSET_NAME_PREFIX = "AutoUploaded_" # leave blank to retain the original filename
OUTPUT_FILE = os.path.basename(os.path.normpath(UPLOAD_FOLDER)) + ".json"
FAILED_POLL_FILE = r"failed_polls.json" # omitting the path will save the file in your user folder

UPLOAD_URL = "https://apis.roblox.com/assets/v1/assets"
HEADERS = {
    "x-api-key": API_KEY
}

# Waitlist for polling
waitlist = []

def is_supported_image(file):
    return file.lower().endswith((".png", ".jpg", ".jpeg"))

def poll_operation(operation_url, max_wait=15, retries=3):
    # Polls the operation endpoint to retrieve the asset ID, with retries.
    for attempt in range(retries):
        for _ in range(max_wait):
            resp = requests.get(operation_url, headers=HEADERS)
            if resp.status_code != 200:
                print(f"[ERROR] Polling failed: {resp.status_code} {resp.text}")
                break

            data = resp.json()
            if data.get("done"):
                asset_id = data.get("response", {}).get("assetId")
                if asset_id:
                    return asset_id
                else:
                    print("[WARN] Polling done, but no asset ID.")
                    break
            sleep(1)

        if attempt < retries - 1:
            delay = 3 * (attempt + 1)
            print(f"[RETRY] Waiting {delay}s before next polling attempt...")
            sleep(delay)

    return None

def upload_image(filepath, name):
    try:
        if filepath.lower().endswith(".png"):
            mime_type = "image/png"
        elif filepath.lower().endswith((".jpg", ".jpeg")):
            mime_type = "image/jpeg"
        else:
            print(f"[SKIP] Unsupported format: {filepath}")
            return None

        with open(filepath, "rb") as image_file:
            request_json = {
                "assetType": "Image",
                "displayName": name,
                "description": "",
                "creationContext": {
                    "creator": {
                        CREATOR_TYPE + "Id": int(CREATOR_ID)
                    }
                }
            }

            files = {
                "request": (None, json.dumps(request_json), "application/json"),
                "fileContent": (os.path.basename(filepath), image_file, mime_type)
            }

            response = requests.post(UPLOAD_URL, headers=HEADERS, files=files)

            if response.status_code == 200:
                resp = response.json()
                operation_path = resp.get("path")
                if not operation_path:
                    print(f"[ERROR] No operation path returned for '{name}'.")
                    return None

                operation_url = f"https://apis.roblox.com/assets/v1/{operation_path}"
                print(f"[WAITLIST] Adding '{name}' to queue...")
                waitlist.append((name, operation_url))
                return None
            else:
                print(f"[ERROR] Upload failed for {name}: {response.status_code} {response.text}")
                return None

    except Exception as e:
        print(f"[EXCEPTION] {filepath}: {str(e)}")
        return None

def retry_waitlist(asset_ids):
    print(f"\n[INFO] Re-polling {len(waitlist)} waitlisted assets...")
    failed_polls = []
    for name, url in waitlist:
        asset_id = poll_operation(url)
        if asset_id:
            print(f"[SUCCESS] '{name}' => Asset ID: {asset_id}")
            asset_ids[name] = asset_id
        else:
            print(f"[FAILED] Could not get Asset ID for '{name}'.")
            failed_polls.append({"name": name, "operation_url": url})

    # Save failed polls to JSON for later correction
    if failed_polls:
        with open(FAILED_POLL_FILE, "w") as f:
            json.dump(failed_polls, f, indent=4)
        print(f"[INFO] Saved {len(failed_polls)} failed polls to '{FAILED_POLL_FILE}'")

def main():
    if not os.path.exists(UPLOAD_FOLDER):
        print(f"[ERROR] Folder '{UPLOAD_FOLDER}' not found.")
        return

    asset_ids = {}
    files = os.listdir(UPLOAD_FOLDER)
    image_files = [f for f in files if is_supported_image(f)]

    if not image_files:
        print("[INFO] No image files found.")
        return

    print(f"[INFO] Uploading {len(image_files)} images...")

    for i, file in enumerate(image_files, 1):
        filepath = os.path.join(UPLOAD_FOLDER, file)
        asset_name = f"{ASSET_NAME_PREFIX}{os.path.splitext(file)[0]}"
        print(f"[{i}/{len(image_files)}] Uploading {file}...")

        asset_id = upload_image(filepath, asset_name)
        if asset_id:
            asset_ids[file] = asset_id

        sleep(0.5)

    # Try polls on waitlist
    retry_waitlist(asset_ids)

    # Save successful uploads
    with open(OUTPUT_FILE, "w") as f:
        json.dump(asset_ids, f, indent=4)

    print("\n=== Upload Summary ===")
    for file, aid in asset_ids.items():
        print(f"{file} => {aid}")

    print(f"\n[INFO] Saved asset IDs to '{OUTPUT_FILE}'")

if __name__ == "__main__":
    main()
