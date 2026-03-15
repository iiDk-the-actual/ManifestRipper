import requests
import zipfile
import io
import os
import re
import shutil

def download_branch(branch_name):
    repo = "SteamAutoCracks/ManifestHub"
    url = f"https://github.com/{repo}/archive/refs/heads/{branch_name}.zip"

    print("Ultimate Manifest Downloader")
    print(f"Downloading branch '{branch_name}' from {repo}...")
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to download branch '{branch_name}'. HTTP Status Code: {response.status_code}")
        return

    temp_dir = f"{branch_name}_temp"
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        zip_file.extractall(temp_dir)

    # Find the first folder inside temp_dir
    extracted_folders = [f for f in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, f))]
    if not extracted_folders:
        print("No folder found in the extracted archive.")
        return

    first_folder_path = os.path.join(temp_dir, extracted_folders[0])

    # Create RippedOutput and move contents
    output_dir = "RippedOutput"
    os.makedirs(output_dir, exist_ok=True)

    for item in os.listdir(first_folder_path):
        src = os.path.join(first_folder_path, item)
        dst = os.path.join(output_dir, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    print(f"Files extracted to './{output_dir}' successfully.")

    # Optional cleanup
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    while True:
        branch = input("Enter Steam Game, Bundle, or Wishlist: ").strip()

        if "/bundle/" in branch:
            match = re.search(r'/bundle/(\d+)', branch)
            if match:
                url = "https://store.steampowered.com/actions/ajaxresolvebundles"
                params = {
                    "bundleids": str(match.group(1)),
                    "cc": "UA",
                    "l": "english"
                }

                # Make the GET request
                response = requests.get(url, params=params)
                response.raise_for_status()

                # Parse the response JSON (a list of bundles)
                bundles = response.json()

                # Collect all app IDs
                all_app_ids = []
                for bundle in bundles:
                    app_ids = bundle.get("appids", [])
                    all_app_ids.extend(app_ids)

                # Output the results
                for appid in all_app_ids:
                    download_branch(appid)
        elif "/wishlist/" in branch:
            url = f"https://api.steampowered.com/IWishlistService/GetWishlist/v1?steamid=76561198874376299"
            response = requests.get(url)
            
            if response.status_code != 200:
                print("Failed to fetch wishlist: ", response.status_code)
            
            data = response.json()
            items = data.get("response", {}).get("items", [])
            appids = [item["appid"] for item in items]
            for appid in appids:
                download_branch(appid)
        elif "/app/" in branch:
            match = re.search(r'/app/(\d+)', branch)
            if match:
                download_branch(match.group(1))
        elif branch == "exit":
            break
        else:
            download_branch(branch)