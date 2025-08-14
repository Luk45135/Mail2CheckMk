import os
from pathlib import Path
from configparser import ConfigParser, SectionProxy
from dataclasses import dataclass
from re import search, sub, Match
from time import time

from mail2text import Email



def get_plaintext_emails() -> list[Path]:
    """This returns a sorted list of all Path objects of the text files in the plaintext-emails directory"""

    plaintext_email_directory = Path("plaintext-emails")
    plaintext_email_list = list(plaintext_email_directory.glob("*.txt"))
    # This sorts the list with the unix timestamp from the filename
    return sorted(plaintext_email_list, key=lambda p: float(p.stem.split("_")[-1].replace(",", ".")))


def get_service_configs() -> list[SectionProxy]:
    """This returns a list of all service config files as parsed configs"""

    service_configs: list[SectionProxy] = []
    config_directory = Path("config/services")
    for config_file in config_directory.glob("*.cfg"):
        cfgparser = ConfigParser()
        cfgparser.read(config_file)
        service_config = cfgparser["Service"]

        service_configs.append(service_config)


    return service_configs


def get_email_from_path(email_path: Path) -> Email:
    """This reads the plaintext email from the path and returns
    it in the form on an Email object from mail2text"""

    email_text: str = email_path.read_text()
    # We keepends here because we want them for the mail body but strip them from the From field and the subject
    email_line_list : list[str] = email_text.splitlines(keepends=True)
    email_from = email_line_list[0].strip()
    subject = email_line_list[2].strip()

    email_body: str = ""

    for email_line in range(4, len(email_line_list)):
        email_body += email_line_list[email_line]

    email_object = Email(email_from, subject, email_body)
    return email_object


@dataclass
class Service:
    delete: bool
    send: bool
    status: int
    name: str
    values: dict
    status_details: str



def create_service_object(service_config: SectionProxy, email_object: Email, subject_match: Match, timestamp: float) -> Service | None:
    """This returns a Service object from the passed info that is fully parsed"""

    status: int = 3

    ok_regex = service_config.get("ok_regex")
    warn_regex = service_config.get("warn_regex")
    crit_regex = service_config.get("crit_regex")

    value_name = service_config.get("value_name")
    value_regex = service_config.get("value_regex")


    ok_match = search(ok_regex, email_object.body) if ok_regex else None
    warn_match = search(warn_regex, email_object.body) if warn_regex else None
    crit_match = search(crit_regex, email_object.body) if crit_regex else None
    relevant_match: Match = search("", email_object.body)


    if crit_match is not None:
        status = 2
        relevant_match = crit_match
    elif warn_match is not None:
        status = 1
        relevant_match = warn_match
    elif ok_match is not None:
        status = 0
        relevant_match = ok_match
    else:
        return None

    warn_cycle: int = service_config.getint("warn_cycle")
    crit_cycle: int = service_config.getint("crit_cycle")
    time_difference: float = time() - timestamp

    if crit_cycle != 0 and time_difference >= crit_cycle:
        status = 2
    elif warn_cycle != 0 and time_difference >= warn_cycle:
        status = 1


    name: str = service_config.get("name").replace("EMAIL_SUBJECT_REGEX", subject_match.group(1))

    values: dict = {}
    if value_name is not None and value_regex is not None:
        values[value_name] = value_regex


    details: str = ""
    match status:
        case 0:
            details = (service_config.get("ok_details")
                       .replace("EMAIL_SUBJECT_REGEX", subject_match.group(1))
                       .replace("REGEX_GROUP", relevant_match.group(1))
                       )
        case 1:
            details = (service_config.get("warn_details")
                       .replace("EMAIL_SUBJECT_REGEX", subject_match.group(1))
                       .replace("REGEX_GROUP", relevant_match.group(1))
                       )
        case 2:
            details = (service_config.get("crit_details")
                       .replace("EMAIL_SUBJECT_REGEX", subject_match.group(1))
                       .replace("REGEX_GROUP", relevant_match.group(1))
                       )

    delete: bool = False
    send: bool = True
            
    return Service(delete, send, status, name, values, details)



def process_emails(plaintext_emails_paths: list[Path], service_config_list: list[SectionProxy]) -> tuple[list[Service], list[Path], int, int]:
    """This checks if any service config applies to the email subject, converts them to Service objects with create_service_object()
    and returns a tuple with the Service object list and a bunch of other useful information"""

    service_objects: list[Service] = []
    service_files_created: int = 0
    files_to_be_deleted: list[Path] = []
    email_without_service_count: int = 0

    for email_path in plaintext_emails_paths:
        email_object = get_email_from_path(email_path)
        email_processed = False

        for service_config in service_config_list:
            email_subject_regex = service_config.get("email_subject_regex")
            re_match: Match = search(email_subject_regex, email_object.subject)
            if re_match is not None:
                # We saved the timestamp in the filename with a "," as the seperator
                timestamp: float = float(email_path.stem.split("_")[-1].replace(",", "."))
                service_object: Service | None = create_service_object(service_config, email_object, re_match, timestamp)
                if service_object is not None:
                    service_objects.append(service_object)
                    service_files_created += 1
                    email_processed = True
        if email_processed:
            files_to_be_deleted.append(email_path)
        else:
            email_without_service_count += 1

    return service_objects, files_to_be_deleted, service_files_created, email_without_service_count



def checkmk_services(service_files: list[Service], emails_processed: int, service_files_created: int, email_without_service_count: int) -> list[Service]:
    """This adds checkmk related services to the service list"""

    service_files.append(Service(True,
                                 True,
                                 0,
                                 "[Mail2CheckMK] Stats",
                                 {"emails_processed":emails_processed, "service_files_created":service_files_created},
                                 f"Mail2CheckMK processed {emails_processed} mails and created {service_files_created} service files this run."
                                 )
                         )
    
    if email_without_service_count > 0:
        service_files.append(Service(True,
                                     True,
                                     1,
                                     "[Mail2CheckMK] Emails without service",
                                     {"email_without_service_count":email_without_service_count},
                                     f"Mail2CheckMK couldn't find services for {email_without_service_count} email(s)"
                                     )
                             )

    return service_files


def save_service_files(service_objects: list[Service]) -> None:

    for service_object in service_objects:
        filename: str = sub(r"[\/\0\n\r\s]", "_", service_object.name)
        unix_time_string = str(time()).replace(".", ",")
        filename += f"_{unix_time_string}"
        formatted_dict: str = ""
        for key, value in service_object.values.items():
            if formatted_dict == "":
                formatted_dict += f" {key}={value}"
            else:
                formatted_dict += f"|{key}={value}"
            

        with open(f"service-files/{filename}.txt", "w") as file:
            file.write(f"Delete Service File: {service_object.delete}\n")
            file.write(f"Send to CheckMK: {service_object.send}\n")
            file.write(f'{str(service_object.status)} "{service_object.name}"{formatted_dict} {service_object.status_details}')


def delete_files(files_to_be_deleted: list[Path]) -> None:
    """This deletes every file in the list"""

    for file in files_to_be_deleted:
        if file.exists():
            os.remove(file.absolute().as_posix())

def move_mails_without_service(plaintext_email_paths: list[Path]) -> None:
    """This moves all remaining plaintext-emails into the without-service subdirectory,
    but because the only remaining one's don't have services it's called like this."""

    for file in plaintext_email_paths:
        if file.exists():
            file.rename(file.parent / "without-service" / file.name)


def main(emails_saved: int = 0) -> None:
    plaintext_emails_paths: list[Path] = get_plaintext_emails()
    service_config_list: list[SectionProxy] = get_service_configs()
    service_objects, files_to_be_deleted, service_files_created, email_without_service_count = process_emails(plaintext_emails_paths, service_config_list)
    service_objects: list[Service] = checkmk_services(service_objects, emails_saved, service_files_created, email_without_service_count)
    save_service_files(service_objects)
    delete_files(files_to_be_deleted)
    move_mails_without_service(plaintext_emails_paths)


if __name__ == "__main__":
    main()



