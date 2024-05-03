import os
import sys
import argparse
import json
import asyncio

ROOT_FOLDER_ID = "00000000-0000-0000-0000-000000000000"

def get_full_path(file, current_folder, folders):

    full_path = []

    folder = folders[current_folder["folderID"]]
    full_path.append(folder["fullFolderName"])

    return os.path.join(*reversed(full_path), file["name"])

async def main():
    parser = argparse.ArgumentParser(description='Download an Aster Data Access Project.')
    parser.add_argument("--project-id", type=str, nargs=1, required=True, help="The project ID to download.")
    parser.add_argument("--exec", type=str, nargs=1, required=False, help="The executable name.", default="rwb")
    parser.add_argument("--verbose", default=False, action="store_true", help="Verbose output.")
    parser.add_argument("--no-dry-run", default=False, action="store_true", help="Don't actually download anything")
    parser.add_argument("--destination-path", type=str, nargs=1, required=False, help="The destination path to download the project to.")
    parser.add_argument("--exclude", type=str, nargs='*', required=False, help="The folders excluded")
    parser.add_argument("--include", type=str, nargs='*', required=False, help="The folders included")
    parser.add_argument("--overwrite", default=False, action="store_true", help="Overwrite existing files instead of skip download if file exists and is the same size.")
    parser.add_argument("--workers", type=int, required=False, help="The number of workers to use for downloading files.", default=1)

    args = parser.parse_args(sys.argv[1:])

    project_id = args.project_id[0]
    executable = args.exec[0]
    verbose = args.verbose
    dry_run = not args.no_dry_run
    destination_path = args.destination_path.pop() if args.destination_path else os.getcwd()
    folder_exclude = args.exclude
    folder_include = args.include
    overwrite = args.overwrite
    workers = args.workers

    if verbose:
        print(f"folder included: {folder_include}")
        print(f"folder excluded: {folder_exclude}")

    cmdline = f"{executable} project folders --project {project_id}"

    if verbose:
        print(cmdline)

    proc = await asyncio.create_subprocess_shell(cmdline, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    response = stdout.decode()

    if stderr:
        print(stderr.decode())
        return

    projects = json.loads(response)

    print(f"Downloading project ({project_id}) using {executable} with verbose={verbose}, dry-run={dry_run} and destination path {destination_path} with {workers} workers.")

    folder_queue = []
    read_folders = {}
    files = asyncio.Queue()
    total_files = 0
    total_size = 0.0

    ## Iterate over all folders to build file list

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

        proc = await asyncio.create_subprocess_shell(cmdline, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()

        if not stdout:
            raise Exception(f'Failed to read folder. Empty response from {cmdline}\n[stderr]\n{stderr.decode()}')

        if stderr:
            raise Exception(f'Error returned from {cmdline}\n[stderr]\n{stderr.decode()}')

        response = stdout.decode()

        folder = json.loads(response)

        read_folders[folder_id] = folder_to_read

        for file in folder["files"]:
            file["fullPath"] = get_full_path(file, folder_to_read, read_folders)

            if (file.get("size") != None):
                total_size = total_size + file["size"]
            else:
                print(f"File {file['fileId']} ({file['fullPath']}) has no size...")

            if verbose:
                print(f"Capturing {file['fileId']} ({file['fullPath']})")

            total_files = total_files + 1
            files.put_nowait(file)

        for folder in folder["folders"]:
            if verbose:
                print(f"Capturing {folder['folderID']} ({folder['fullFolderName']})")

            folder_queue.insert(0, folder)

    ## Download files worker
    ##
    ##
    async def download_file_worker(worker_name, file_queue):
        job_count = 1
        while True:
            file = await file_queue.get()

            try:
                if not overwrite:
                    file_path = os.path.join(destination_path,file["fullPath"].lstrip('/'))
                    file_exists = os.path.exists(file_path)
                    file_size = os.stat(file_path).st_size if file_exists else 0
                    if verbose:
                        print(f"{worker_name}:{job_count} | Checking if file {file_path} exists ({file_exists}) and is the same size as {file['size']} ({file_size})")

                    if file_exists and file_size == file["size"]:
                        print(f"{worker_name}:{job_count} | Skipping file {file['fullPath']}, already exists and is the same size")
                        continue

                if dry_run:
                    print(f"{worker_name}:{job_count} | Would download file {file['fullPath']} to {destination_path}{file['fullPath']} - dry-run enabled")
                    continue

                directory = os.path.join(destination_path,os.path.dirname(file["fullPath"]).lstrip('/'))

                if not os.path.exists(directory):
                    if verbose:
                        print(f"{worker_name}:{job_count} | Creating directory {directory}")

                    os.makedirs(directory)

                print(f"{worker_name}:{job_count} | - Downloading file {file['fullPath']}")
                cmdline = f"{executable} file download --file-id {file['fileId']} --path {destination_path}{file['fullPath']}"

                if verbose:
                    print(f"{worker_name}:{job_count} | {cmdline}")

                download_proc = await asyncio.create_subprocess_shell(cmdline, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                stdout, stderr = await download_proc.communicate()

                if not stdout:
                    raise Exception(f'Failed to read folder. Empty response from {cmdline}\n[stderr]\n{stderr.decode()}')

                if stderr:
                    raise Exception(f'Error returned from {cmdline}\n[stderr]\n{stderr.decode()}')

                if verbose:
                    download_output = stdout.decode()
                    print(f"{worker_name}:{job_count} | {download_output}")

            except TimeoutError as e:
                print(f"{worker_name}:{job_count}  - Timeout downloading file {file['fullPath']}")
            except Exception as e:
                print(f"{worker_name}:{job_count}  - Error downloading file {file['fullPath']}: {e}")
            finally:
                job_count = job_count + 1
                file_queue.task_done()

    tasks = []
    for i in range(workers):
        task = asyncio.create_task(download_file_worker(f"worker{i}", files))
        tasks.append(task)

    await files.join()

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

    print(f"Total Files: {total_files:,d}")
    print(f"Total Size: {total_size / 1024.0 / 1024.0 / 1024.0:,.2f} GB")
    return

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))