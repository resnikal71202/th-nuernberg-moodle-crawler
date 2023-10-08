import json
import os
import shutil

json_file_path = "file_structure.json"
source_folder = "downloads"
unknown_folder = "unknown"

# Check if the JSON file exists, if not, create it with an empty list of files
if not os.path.exists(json_file_path):
    with open(json_file_path, "w") as json_file:
        json.dump({"format": "file sorter 0.1.0", "files": []}, json_file, indent=4)

# Load existing JSON data
with open(json_file_path, "r") as json_file:
    data = json.load(json_file)

# Get the list of files in the downloads folder
downloaded_files = os.listdir(source_folder)

# Iterate through downloaded files and process them based on JSON rules
for file_name in downloaded_files:
    file_entry = next(
        (entry for entry in data["files"] if entry["name"] == file_name), None
    )

    # If the file is not in the JSON, add it and move to the unknown folder
    if file_entry is None:
        new_entry = {
            "name": file_name,
            "destination": unknown_folder,
            "last_change": "",
            "overwrite": False,
        }
        data["files"].append(new_entry)
        with open(json_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        shutil.move(
            os.path.join(source_folder, file_name),
            os.path.join(unknown_folder, file_name),
        )
    else:
        # If the file is in the JSON, perform actions based on overwrite flag
        if file_entry["overwrite"]:
            shutil.move(
                os.path.join(source_folder, file_name),
                os.path.join(file_entry["destination"], file_name),
            )
        else:
            os.remove(os.path.join(source_folder, file_name))

print("Files sorted and processed according to the JSON configuration.")
