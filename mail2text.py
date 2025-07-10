from configparser import ConfigParser, SectionProxy
from imaplib import IMAP4
from email import message_from_bytes
from email.message import Message
from email.header import decode_header
from dataclasses import dataclass
from time import time
from bs4 import BeautifulSoup


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

def get_message_numbers_from_inbox(imap_server: IMAP4, mail_config: SectionProxy) -> list[str]:
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


def decode_any_content_type(message: Message) -> str | None:
    """This decodes any message or part of any content type and returns the message body
    if possible"""

    content_type = message.get_content_type()
    payload = message.get_payload(decode=True)
    if not payload:
        return None

    charset = message.get_charset() or "utf-8"
    
    try:
        match content_type:
            case "text/plain":
                return payload.decode(charset)
            case "text/html":
                return BeautifulSoup(payload, "html.parser").get_text(separator="\n", strip=True)
            case _:
                return None
    except Exception:
        return None


def parse_message_body(message: Message) -> str:
    """This parses the message body and sends it to decode_any_content_type and returns the body"""

    body: str = ""
    if message.is_multipart():
        for part in message.walk():
            content_disposition: str = str(part.get_content_disposition())
            if "attachment" in content_disposition:
                continue
            
            text = decode_any_content_type(part)
            if text:
                body += text + "\n"
    else:
        text = decode_any_content_type(message)
        if text:
            body = text
    
    return body.strip() if body.strip() else "(no readable content)"


def get_messages_from_message_nums(message_number_list: list[str], imap_server: IMAP4) -> list[Email]:
    """This gets all messages from the message numbers from the server, parses them
    and returns them in a list"""

    emails: list[Email] = []

    for message_num in message_number_list:

        status, data = imap_server.fetch(message_num, "(RFC822)")
    
        raw_email: bytes = data[0][1]
        # print(raw_email)
    
        msg = message_from_bytes(raw_email)
    
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")
    
        from_field = msg.get("From")
    
        body = parse_message_body(msg) 
        # payload = msg.get_payload(decode=True)
        # charset = msg.get_content_charset() or "utf-8"
        # body = payload.decode(charset)
    
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
        unix_time_string = str(time()).replace(".", "-")
        filename_prefix = email.subject.replace(" ", "_")
        with open(f"plaintext-emails/{filename_prefix}_{unix_time_string}.txt", "w") as file:
            file.write(f"{email.from_field}\n")
            file.write("\n")
            file.write(f"{email.subject}\n")
            file.write("\n")
            file.write(email.body)


    

def logout_from_imap_server(imap_server: IMAP4) -> None:
    """This closes any mailbox, logs out
    and closes the connection to the passed IMAP server"""

    imap_server.close()
    imap_server.logout()

def main():
    mail_config: SectionProxy = read_config()
    imap_server: IMAP4 = connect_to_imap_server(mail_config)
    message_number_list: list[str] = get_message_numbers_from_inbox(imap_server, mail_config)
    emails: list[Email] = get_messages_from_message_nums(message_number_list, imap_server)
    save_emails_as_plaintext(emails)

    logout_from_imap_server(imap_server)

if __name__ == "__main__":
    main()

