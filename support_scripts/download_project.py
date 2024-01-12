import os
import subprocess
import sys
import argparse
import json

ROOT_FOLDER_ID = "00000000-0000-0000-0000-000000000000"

def get_full_path(file, current_folder, folders):

    full_path = []

    folder = folders[current_folder["folderID"]]
    full_path.append(folder["fullFolderName"])

    return os.path.join(*reversed(full_path), file["name"])

def main():
    parser = argparse.ArgumentParser(description='Download an Aster Data Access Project.')
    parser.add_argument("--project-id", type=str, nargs=1, required=True, help="The project ID to download.")
    parser.add_argument("--exec", type=str, nargs=1, required=False, help="The executable name.", default="rwb")
    parser.add_argument("--verbose", default=False, action="store_true", help="Verbose output.")
    parser.add_argument("--no-dry-run", default=False, action="store_true", help="Don't actually download anything")
    parser.add_argument("--destination-path", type=str, nargs=1, required=False, help="The destination path to download the project to.")
    parser.add_argument("--exclude", type=str, nargs='*', required=False, help="The folders excluded")
    parser.add_argument("--include", type=str, nargs='*', required=False, help="The folders included")
    parser.add_argument("--overwrite", default=False, action="store_true", help="Overwrite existing files instead of skip download if file exists and is the same size.")

    args = parser.parse_args(sys.argv[1:])

    project_id = args.project_id[0]
    executable = args.exec[0]
    verbose = args.verbose
    dry_run = not args.no_dry_run
    destination_path = args.destination_path.pop() if args.destination_path else os.getcwd()
    folder_exclude = args.exclude
    folder_include = args.include
    overwrite = args.overwrite

    if verbose:
        print(f"folder included: {folder_include}")
        print(f"folder excluded: {folder_exclude}")

    cmdline = f"{executable} project folders --project {project_id}"

    if verbose:
        print(cmdline)

    projects = json.loads(subprocess.check_output(cmdline, shell=True, stderr=subprocess.STDOUT))

    print(f"Downloading project ({project_id}) using {executable} with verbose={verbose}, dry-run={dry_run} and destination path {destination_path}")

    folder_queue = []
    read_folders = {}
    files = []
    total_files = 0
    total_size = 0.0

    for folder in projects["folders"]:
        if verbose:
            print(f"Capturing {folder['folderID']} ({folder['fullFolderName']})")
        
        folder_queue.insert(0, folder)

    while len(folder_queue) > 0:
        folder_to_read = folder_queue.pop()
        folder_id = folder_to_read["folderID"]

        print(f"Reading folder {folder_id} ({folder_to_read['fullFolderName']})")

        if folder_include:
            if not any(folder_to_read['fullFolderName'].startswith(include) for include in folder_include):
                if verbose:
                    print(f"Folder {folder_to_read['fullFolderName']} not included")
                continue

        if folder_exclude:
            if any(folder_to_read['fullFolderName'].startswith(exclude) for exclude in folder_exclude):
                print(f"Folder {folder_to_read['fullFolderName']} excluded")
                continue

        if folder_id in read_folders:
            if verbose:
                print(f"Folder {folder_id} already read, skipping")
            
            continue

        cmdline = f"{executable} project files --project {project_id} --folder-id {folder_id}"

        if verbose:
            print(cmdline)
        
        folder = json.loads(subprocess.check_output(cmdline, shell=True, stderr=subprocess.STDOUT))
        
        read_folders[folder_id] = folder_to_read

        for file in folder["files"]:
            file["fullPath"] = get_full_path(file, folder_to_read, read_folders)

            if (file.get("size") != None):
                total_size = total_size + file["size"]
            else:
                print(f"File {file['fileId']} ({file['fullPath']}) has no size...")

            if verbose:
                print(f"Capturing {file['fileId']} ({file['fullPath']})")

            files.append(file)

        for folder in folder["folders"]:
            if verbose:
                print(f"Capturing {folder['folderID']} ({folder['fullFolderName']})")
            
            folder_queue.insert(0, folder)
    
    for file in files:
        if dry_run:
            print(f"Would download file {file['fullPath']} to {destination_path}{file['fullPath']} - dry-run enabled")
            continue
        
        directory = os.path.join(destination_path,os.path.dirname(file["fullPath"]).lstrip('/'))

        if not os.path.exists(directory):
            if verbose:
                print(f"Creating directory {directory}")

            os.makedirs(directory)
        
        if not overwrite:
            file_path = os.path.join(destination_path,file["fullPath"].lstrip('/'))
            file_exists = os.path.exists(file_path)
            file_size = os.stat(file_path).st_size if file_exists else 0
            if verbose:
                print(f"Checking if file {file_path} exists ({file_exists}) and is the same size as {file['size']} ({file_size})")

            if file_exists and file_size == file["size"]:
                print(f"Skipping file {file['fullPath']}, already exists and is the same size")
                continue

        print(f"Downloading file {file['fullPath']} to {destination_path}{file['fullPath']}")
        cmdline = f"{executable} file download --file-id {file['fileId']} --path {destination_path}{file['fullPath']}"
        
        if verbose:
            print(cmdline)
        
        download_output = subprocess.check_output(cmdline, shell=True, stderr=subprocess.STDOUT)

        if verbose:
            print(download_output)

    print(f"Total Files: {len(files):,d}")
    print(f"Total Size: {total_size / 1024.0 / 1024.0 / 1024.0:,.2f} GB")
    return

if __name__ == "__main__":
    sys.exit(main())