from pathlib import Path
from configparser import ConfigParser, SectionProxy


def get_plaintext_emails() -> list[Path]:

    plaintext_email_directory = Path("plaintext-emails")
    plaintext_email_iterator = plaintext_email_directory.glob("*.txt")
    return list(plaintext_email_iterator)


def get_service_configs() -> list[SectionProxy]:
    service_configs: list[SectionProxy] = []
    config_directory = Path("config/services")
    for config_file in config_directory.glob("*.cfg"):
        cfgparser = ConfigParser()
        cfgparser.read(config_file)
        service_config = cfgparser["Service"]

        service_configs.append(service_config)


    return service_configs


def main() -> None:
    plaintext_emails: list[Path] = get_plaintext_emails()
    service_configs: list[SectionProxy] = get_service_configs()


if __name__ == "__main__":
    main()
