import prepare
import mail2text

def main() -> None:
    prepare.main()
    mails_processed: int = mail2text.main()


if __name__ == "__main__":
    main()
