# RBLXImageUpload
RBLXImageUpload enables you to bulk upload `.png`, `.jpg` and `.jpeg` files using secure [OpenCloud API keys](https://create.roblox.com/docs/en-us/cloud/auth/api-keys) with a simple Python script.

## Features

- Bulk upload `.png`, `.jpg`, `.jpeg` images from a folder
- Automatically polls operation URLs until asset ID is ready
- Retries polling if metadata isn’t ready yet (with backoff)
- Failed polls saved for later retry
- Another script for retrying failed polls

## Requirements

- [Python 3.8+](https://www.python.org/downloads)
- Roblox Open Cloud API key (with asset read, write permissions)
- `requests` Python package (`pip install requests`)

## Usage
### Upload Assets
First, you'll need to create some credentials so that the uploader can upload in your name:
1. **Generate an API key** from your [creator dashboard](https://create.roblox.com/dashboard/credentials). Ensure you view the page from the group/user you want to upload to.
2. Set the key settings to your needs, but make sure to add the `assets` API System, assigning it both the `read` and `write` operations.
3. Generate the API key and copy the secret somewhere safe.

Now that you have the key, make sure Python and the `requests` package are both installed (reopen the command prompt after installing).
1. Download [upload.py](/upload.py)
2. Open the script in any editor or notepad
3. Modify the following variables (you can leave the last three as default):
```py
API_KEY = "your-api-key"
CREATOR_TYPE = "group"  # group or user, check under who you were creating the key
CREATOR_ID = "your-id-here"  # your group or user ID, find it in Roblox URLs
UPLOAD_FOLDER = r"path-to-your-folder"  # enter the path to the folder that contains your assets to upload
ASSET_NAME_PREFIX = "AutoUploaded_" # leave blank to retain the original filename
OUTPUT_FILE = os.path.basename(os.path.normpath(UPLOAD_FOLDER)) + ".json" # you can change this to a custom path, by default it creates a json with the filename of UPLOAD_FOLDER inside your user folder
FAILED_POLL_FILE = r"failed_polls.json" # omitting the path will save the file in your user folder
```
4. Save the script and open the command prompt, typing in and running
```bash
python path-to-uploader.py
```
After the script finishes uploading, you can retrieve your asset IDs from the `OUTPUT_FILE` you've set before
### Retry Failed Uploads
If some asset polls failed (e.g., due to API latency), download the [retry script](/reupload.py), fill in constants like before, and run:
```bash
python path-to-reuploader.py
```
If there are still some failed uploads after retrying without errors from incompatible files, wait a bit and try again later, as it's a common occurrence in bulk uploading for Roblox's backend to hold up files for further processing.
### Example Output
```json
{
  "Amanda": "84072324915477",
  "Bob": "84072324916455"
}
```

## Contributing
Pull requests and suggestions welcome! For now, these scripts only handle image uploading, but they can be easily modified for uploading all types of assets, listed on these [Open Cloud docs](https://create.roblox.com/docs/cloud/guides/usage-assets#supported-asset-types-and-limits).

## Official API Documentation
[Open Cloud Assets](https://create.roblox.com/docs/cloud/features/assets)

[Open Cloud v1 Assets API](https://create.roblox.com/docs/reference/cloud/assets/v1)

[Usage guide for assets](https://create.roblox.com/docs/cloud/guides/usage-assets)
