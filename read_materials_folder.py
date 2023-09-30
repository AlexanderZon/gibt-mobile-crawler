import os
import json

# Specify the directory path you want to read filenames from
directory_path = './.data/materials'

# Initialize an empty list to store the filenames without extensions
file_names_without_extension = []

# Check if the specified path is a directory
if os.path.isdir(directory_path):
    # Use os.listdir() to get a list of filenames in the directory
    file_names = os.listdir(directory_path)
    
    # Remove file extensions
    for file_name in file_names:
        name_without_extension, _ = os.path.splitext(file_name)
        file_names_without_extension.append(name_without_extension)
else:
    print(f"The path '{directory_path}' is not a valid directory.")

# Define the JSON file path where you want to write the data
json_file_path = '.data/materials_file_names.json'

# Write the list of filenames without extensions to a JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(file_names_without_extension, json_file)
