# This module makes sure that the needed directory structure
# for the other modules exists

from pathlib import Path

def main() -> None:

    Path("plaintext-emails/without-service").mkdir(parents=True, exist_ok=True)
    Path("service-files").mkdir(parents=True, exist_ok=True)



if __name__ == "__main__":
    main()
