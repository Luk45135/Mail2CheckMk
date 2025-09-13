# This is the entry point of the program which
# executes every module in order

import prepare
import mail2text
import textmail2service
import service2checkmk



def main() -> None:
    prepare.main()
    emails_saved: int = mail2text.main()
    textmail2service.main(emails_saved)
    service2checkmk.main()



if __name__ == "__main__":
    main()
