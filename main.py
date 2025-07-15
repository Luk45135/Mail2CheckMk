import prepare
import mail2text
import textmail2service
import service2checkmk



def main() -> None:
    prepare.main()
    mails_processed: int = mail2text.main()
    textmail2service.main()
    service2checkmk.main()



if __name__ == "__main__":
    main()
