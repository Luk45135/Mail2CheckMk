# This module downloads all Emails from the configured IMAP4 server,
# saves them as plaintext-files in ./plaintext-emails,
# and then either moves or deletes them on the IMAP server

from configparser import ConfigParser, SectionProxy
from imaplib import IMAP4, IMAP4_SSL
from email import message_from_bytes
from email.message import Message
from email.header import decode_header
from dataclasses import dataclass
from re import sub
from time import time
from bs4 import BeautifulSoup
from typing import Union

# SSL and Non-SSL use different classes
# So to preserver type annotation a Union is used
IMAPServer = Union[IMAP4, IMAP4_SSL]


def read_config() -> SectionProxy:
    """This reads the config file at config/config.cfg
    and returns the config object for the 'Email' section"""

    cfgparser = ConfigParser()
    cfgparser.read("config/config.cfg")
    mail_config = cfgparser["Mail"]

    return mail_config


def connect_to_imap_server(mail_config: SectionProxy) -> IMAPServer:
    """This connects to the IMAP server using the configured connection type"""

    imap_host = mail_config.get("host", "localhost")
    imap_port = mail_config.getint("port", 143)
    use_ssl = mail_config.getboolean("use_ssl", False)
    use_starttls = mail_config.getboolean("use_starttls", False)

    if use_ssl:
        imap_server = IMAP4_SSL(host=imap_host, port=imap_port)
    else:
        imap_server = IMAP4(host=imap_host, port=imap_port)
        if use_starttls:
            imap_server.starttls()

    return imap_server



def login_to_imap(imap_server: IMAPServer, mail_config: SectionProxy) -> IMAPServer:
    """This logs in to the IMAP Server with the configured details"""
    
    imap_user = mail_config.get("user", "testuser")
    imap_password = mail_config.get("password", "testpass")
    imap_server.login(user=imap_user, password=imap_password)

    return imap_server


def get_message_numbers_from_inbox(imap_server: IMAPServer, mail_config: SectionProxy) -> list[str]:
    """This gets all emails/message id's/numbers from the passed IMAP server
    from the configured Inbox mailbox and returns them in a list"""

    imap_server.select(mail_config.get("inbox", "INBOX"))
    
    status, message_numbers = imap_server.search(None, "ALL")

    message_number_list = message_numbers[0].split() if message_numbers else []

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


def get_messages_from_message_nums(message_number_list: list[str], imap_server: IMAPServer) -> list[Email]:
    """This gets all messages from the message numbers from the server, parses them
    and returns them in a list"""

    emails: list[Email] = []

    for message_num in message_number_list:

        status, data = imap_server.fetch(message_num, "(RFC822)")
    
        raw_email: bytes = data[0][1]
    
        msg = message_from_bytes(raw_email)
    
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")
    
        from_field = msg.get("From")
    
        body = parse_message_body(msg) 
    
        email = Email(
                from_field = str(from_field),
                subject = subject,
                body = body
                )
        emails.append(email)

    return emails

def save_emails_as_plaintext(emails: list[Email]) -> int:
    """This saves all emails passed in as a plaintext file
    and returns the number of emails saved this way"""

    emails_saved: int = 0
    for email in emails:
        unix_time_string = str(time()).replace(".", ",")
        filename_prefix = sub(r"[\/\0\n\r\s]", "_", email.subject)
        with open(f"plaintext-emails/{filename_prefix}_{unix_time_string}.txt", "w") as file:
            file.write(f"{email.from_field}\n")
            file.write("\n")
            file.write(f"{email.subject}\n")
            file.write("\n")
            file.write(email.body)

        emails_saved += 1

    return emails_saved


def move_emails(imap_server: IMAPServer, message_nums: list[str], mail_config: SectionProxy) -> None:
    """This copies the messages to the configured target mailbox if configured to do so
    and then deletes them from the Inbox"""
    archive_mails: bool = mail_config.getboolean("archive_processed_mails")

    for msg_num in message_nums:
        if archive_mails:
            imap_server.copy(msg_num, mail_config.get("archive_mailbox"))

        imap_server.store(msg_num, "+FLAGS", r"(\Deleted)")

    imap_server.expunge()
    

def logout_from_imap_server(imap_server: IMAPServer) -> None:
    """This closes any mailbox, logs out
    and closes the connection to the passed IMAP server"""

    imap_server.close()
    imap_server.logout()

def main() -> int:
    mail_config: SectionProxy = read_config()
    imap_server: IMAPServer = connect_to_imap_server(mail_config)
    imap_server: IMAPServer = login_to_imap(imap_server, mail_config)
    message_number_list: list[str] = get_message_numbers_from_inbox(imap_server, mail_config)
    emails: list[Email] = get_messages_from_message_nums(message_number_list, imap_server)
    mails_saved: int = save_emails_as_plaintext(emails)
    move_emails(imap_server, message_number_list, mail_config)

    logout_from_imap_server(imap_server)
    return mails_saved

if __name__ == "__main__":
    main()

