from datetime import datetime
import logging
import os
import shutil
import json
import time

# Set up logging
log_file = "transfer_log.txt"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# Load configuration from a JSON file
config_file = "config.json"

def load_config():
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found. Please create the config file with the required settings.")
        exit()

config = load_config()

# Source and destination directories
# source_directory = config.get('source_directory', "G:/MBA Course")
source_directory = config.get('source_directory')
# destination_directory = config.get('destination_directory', "D:/Transferred_from_G2/destination")
destination_directory = config.get('destination_directory')


# source_directory =  "G:\MBA Course"
# destination_directory = "D:\Transferred_from_G2\destination"


# upper_limit_folder_size = 6900000000    # 6.5GB
upper_limit_folder_size = config.get('upper_limit_folder_size')




#  get folder size in bytes
def get_folder_size(path):
    total_size = 0

    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)

    return total_size


def copy_oldest_folders():
    folders = []

    for root, dirs, files in os.walk(source_directory, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            folders.append((dir_path, os.path.getctime(dir_path)))
            # print("folders list: ",folders)


    folders.sort(key=lambda x: x[1])
    print(f"{len(folders)} folders to be transferred: ")
    for num, folder_data in enumerate(folders):
        folder, date_created = folder_data
        # date_created_formatted = date_created.strftime("%Y-%m-%d %H:%M:%S")
        date_created_formatted = datetime.fromtimestamp(date_created).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{num}: {folder}\t {date_created_formatted}")
    # source_folder_size = get_folder_size(source_directory)
    initial_source_folder_size = get_folder_size(source_directory)
    copied_folders = []
    transferred_size = 0


    for folder, create_date in folders:
            if  transferred_size >= initial_source_folder_size - upper_limit_folder_size:
                break
            source_folder = folder
            destination_folder = os.path.join(destination_directory, os.path.basename(folder))

            # Check if the source folder still exists
            if os.path.exists(source_folder):
                try:
                    print(f"copying folder: {source_folder}\t from ---> {source_directory} ---- to ---> {destination_directory}")
                    source_folder_size = get_folder_size(source_folder)/1048576
                    shutil.copytree(source_folder, destination_folder)
                    transferred_size += get_folder_size(source_folder)
                    copied_folders.append(source_folder)
                    print(f"removing folder: {source_folder}\t from source directory > {source_directory}")
                    shutil.rmtree(source_folder)  # Remove the source folder to free up space
                    # Log the transfer details
                    logging.info(f"Created: {datetime.fromtimestamp(create_date)}, Size: {source_folder_size:.2f} MB, Transferred Folder: {os.path.basename(source_folder)}" )
                except FileExistsError:
                    pass  # Folder already exists in the destination directory


    return copied_folders, transferred_size/1048576  # Return the transferred size in MB

# Main script
if __name__ == "__main__":
    while True: 
        transferred_size = 0
        current_source_folder_size = get_folder_size(source_directory)/1048576
        # added
        print(f"source folder size: {current_source_folder_size:.2f} MB")
        current_destination_folder_size = get_folder_size(destination_directory)/1048576
        print(f"destination folder size: {current_destination_folder_size:.2f} MB")

        # finish added
        if current_source_folder_size >= upper_limit_folder_size/1048576:
            copied_folders, transferred_size = copy_oldest_folders()
            if copied_folders:
                print("Folders copied to free up source space:")
                for folder in copied_folders:
                    print(folder)
            else:
                print("No folders were copied.")
        else:
            print("Disk space is not low.")


        current_source_folder_size = get_folder_size(source_directory)/1048576
        # added
        print(f"source folder size: {current_source_folder_size:.2f} MB")
        current_destination_folder_size = get_folder_size(destination_directory)/1048576
        print(f"destination folder size: {current_destination_folder_size:.2f} MB")
        print(f"transferred size: {transferred_size:.2f} MB ")

        # Sleep for 3 hours (3 hours * 60 minutes * 60 seconds)
        time.sleep(3 * 60)







