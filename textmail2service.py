from pathlib import Path
from configparser import ConfigParser, SectionProxy
from mail2text import Email
from dataclasses import dataclass
import re


def get_plaintext_emails() -> list[Path]:
    """This returns a list of all Path objects of the text files in the plaintext-emails directory"""

    plaintext_email_directory = Path("plaintext-emails")
    plaintext_email_iterator = plaintext_email_directory.glob("*.txt")
    return list(plaintext_email_iterator)


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
    status: int
    name: str
    values: dict
    status_details: str

@dataclass
class ServiceFile(Service):
    processed: bool



def process_emails(plaintext_emails_paths: list[Path], service_config_list: list[SectionProxy]) -> None:

    for email_path in plaintext_emails_paths:
        email_object = get_email_from_path(email_path)

        # print(email_object)
        for service_config in service_config_list:
            email_subject_regex = service_config.get("email_subject_regex")
            # print(email_subject_regex)
            # print(email_object.subject)
            re_match = re.match(email_subject_regex, email_object.subject)
            # print(re_match)
            if re_match != None:
                ...
                # print("CHECK")


def main() -> None:
    plaintext_emails_paths: list[Path] = get_plaintext_emails()
    service_config_list: list[SectionProxy] = get_service_configs()
    process_emails(plaintext_emails_paths, service_config_list)


if __name__ == "__main__":
    main()



