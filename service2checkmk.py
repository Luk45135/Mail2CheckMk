from pathlib import Path
from textmail2service import Service, ServiceFile



def get_list_of_service_files() -> list[Path]:
    """This return a list of every text file in service-files/ as Path objects"""
    service_files: list[Path] = []

    for file in Path("service-files").glob("*.txt"):
        service_files.append(file)

    return service_files


def get_object_from_path(service_file: Path) -> ServiceFile:
    ...


def filter_duplicate_services(service_files: list[Path]) -> list[Path]:
    list_of_service_names: list[str] = []
    filtered_service_files: list[Path] = []

    for service in service_files:
        service_object: ServiceFile = get_object_from_path(service)
        service_name: str = service_object.name
        if service_name not in list_of_service_names:
            list_of_service_names.append(service_name)
            filtered_service_files.append(service)

    return filtered_service_files



def main() -> None:
    service_files: list[Path] = get_list_of_service_files()



if __name__ == "__main__":
    main()

