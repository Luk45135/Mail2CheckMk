from configparser import ConfigParser, SectionProxy
from imaplib import IMAP4
from email import message_from_bytes
from email.header import decode_header
from dataclasses import dataclass
from time import time


def read_config() -> SectionProxy:
    """This reads the config file at config/config.cfg
    and returns the config object for the 'Email' section"""

    cfgparser = ConfigParser()
    cfgparser.read("config/config.cfg")
    mail_config = cfgparser["Mail"]

    return mail_config


def connect_to_imap_server(mail_config: SectionProxy) -> IMAP4:
    """This connects to the IMAP server from the passed config details,
    logs in with the provided details and then return the IMAP4 server object"""

    imap_server = IMAP4(host=mail_config.get("host", "localhost"), port=mail_config.getint("port", 143))

    imap_server.login(user=mail_config.get("user", "testuser"), password=mail_config.get("password", "testpass"))

    return imap_server

def get_message_numbers_from_inbox(imap_server: IMAP4, mail_config: SectionProxy) -> list[int]:
    """This gets all emails/message id's/numbers from the passed IMAP server
    from the configured Inbox mailbox and returns them in a list"""

    imap_server.select(mail_config.get("inbox", "INBOX"))
    
    status, message_numbers = imap_server.search(None, "ALL")

    message_number_list = message_numbers[0].split()

    return message_number_list

@dataclass
class Email:
    """A Email object must have the from-field, the subject and the email body defined"""

    from_field: str
    subject: str
    body: str

def get_messages_from_message_nums(message_number_list: list[int], imap_server: IMAP4) -> list[Email]:
    """This gets all messages from the message numbers from the server, parses them
    and returns them in a list"""

    emails: list[Email] = []

    for message_num in message_number_list:
        print(message_num)
        status, data = imap_server.fetch(message_num, "(RFC822)")
    
        raw_email: bytes = data[0][1]
        # print(raw_email)
    
        msg = message_from_bytes(raw_email)
    
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")
    
        from_field = msg.get("From")
    
    
        payload = msg.get_payload(decode=True)
        charset = msg.get_content_charset() or "utf-8"
        body = payload.decode(charset)
    
        email = Email(
                from_field = str(from_field),
                subject = subject,
                body = body
                )
        emails.append(email)

    return emails

def save_emails_as_plaintext(emails: list[Email]) -> None:
    """This saves all emails passed in as a plaintext file"""

    for email in emails:
        ...  

    

def logout_from_imap_server(imap_server: IMAP4) -> None:
    """This closes any mailbox, logs out
    and closes the connection to the passed IMAP server"""

    imap_server.close()
    imap_server.logout()

def main():
    mail_config: SectionProxy = read_config()
    imap_server: IMAP4 = connect_to_imap_server(mail_config)
    message_number_list: list[int] = get_message_numbers_from_inbox(imap_server, mail_config)
    emails: list[Email] = get_messages_from_message_nums(message_number_list, imap_server)
    save_emails_as_plaintext(emails)

    logout_from_imap_server(imap_server)

if __name__ == "__main__":
    main()

