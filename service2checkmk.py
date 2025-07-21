import os
from pathlib import Path
from re import sub


def get_service_files() -> list[Path]:
    """This returns a sorted list of every text file in service-files/ as Path objects"""
    service_files_with_timestamp: list[tuple[Path, float]] = []

    for file in Path("service-files").glob("*.txt"):
        # This gets the timestamp from the filename
        timestamp: float = float(file.stem.split("_")[-1].replace(",", "."))
        service_files_with_timestamp.append((file, timestamp))
    
    sorted_service_files = sorted(service_files_with_timestamp, key=lambda x: x[1])

    # This returns the first element of the tuple t[0] for every tuple in sorted_service_files_with_timestamps
    return [t[0] for t in sorted_service_files]


# def get_object_from_path(service_files: list[Path]) -> list[Service]:
#     ...

def mark_as_processed(service_file_path: Path):
    """This marks a service file as processed/for deletion"""
    
    lines: list[str] = []
    with open(service_file_path, "r") as f:
        lines = f.readlines()

    lines[0] = "True\n"
    with open(service_file_path, "w") as f:
        f.writelines(lines)



def filter_duplicate_services(service_files: list[Path]) -> list[Path]:
    """This makes sure that only 1 service with the same name is returned in the list
    and marks any duplicate as processed/for deletion"""

    list_of_service_names: list[str] = []
    filtered_service_files: list[Path] = []

    for service in service_files:
        # service_object: Service = get_object_from_path(service)
        # service_name: str = service_object.name
        filename_stem: str = service.stem
        service_name: str = sub(r"_\d{10,},", "", filename_stem)

        if service_name not in list_of_service_names:
            list_of_service_names.append(service_name)
            filtered_service_files.append(service)
        else:
            mark_as_processed(service)
            

    return filtered_service_files


def send_to_checkmk(service_files: list[Path]) -> None:
    """This prints the second line to standard out"""

    for file in service_files:
        checkmk_output: list[str] = file.read_text().splitlines()
        print(checkmk_output[1])

def mark_services_with_ok_status_as_processed(filtered_service_files: list[Path]) -> None:
    """This sends any service file that has a 0 status code to mark_as_processed()"""
    
    for file in filtered_service_files:
        lines: list[str] = []
        with open(file, "r") as f:
            lines = f.readlines()
        # The status code of a service file is saved in the first position of the second line
        if lines[1][0] == "0":
            mark_as_processed(file)


def delete_service_files(service_files: list[Path]) -> None:
    """This deletes every file that has been marked as processed/for deletion"""

    for file in service_files:
        lines: list[str] = []
        with open(file, "r") as f:
            lines = f.readlines()
        if lines[0] == "True\n":
            os.remove(file.absolute().as_posix())



def main() -> None:
    service_files: list[Path] = get_service_files()
    filtered_service_files: list[Path] = filter_duplicate_services(service_files)
    send_to_checkmk(filtered_service_files)
    mark_services_with_ok_status_as_processed(filtered_service_files)
    delete_service_files(service_files)



if __name__ == "__main__":
    main()

