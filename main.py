import email
import imaplib
import re
from datetime import datetime
from email.header import decode_header
from email.utils import parsedate_to_datetime
from os import getenv

import notify2
import pyclip
from dotenv import load_dotenv

load_dotenv()
USERNAME = getenv("IMAP_USERNAME")
IMAP_PASSWORD = getenv("IMAP_PASSWORD")
IMAP_SERVER = getenv("IMAP_SERVER")
SEARCH_SUBJECT = "account verification code"


def get_latest_email_body_by_subject(username, password, server, subject):
    """
    Connects to an IMAP server, finds the latest email with a specific subject,
    and returns its body.
    """
    try:
        # Connect to the server over SSL
        print(f"Connecting to {server}...")
        mail = imaplib.IMAP4_SSL(server)

        # Login to your account
        print("Logging in...")
        mail.login(username, password)

        # Select the mailbox you want to check (e.g., 'inbox')
        mail.select("inbox")
        print("Inbox selected.")

        # Search for emails with the specified subject
        # Note: The search string must be formatted correctly.
        print(f"Searching for emails with subject: '{subject}'...")
        status, messages = mail.search(None, f'(SUBJECT "{subject}")')

        if status != "OK":
            print("No messages found!")
            return None

        # The 'messages' variable contains a list of email IDs
        # The IDs are returned as a space-separated string in a list, e.g., [b'1 2 3']
        email_ids = messages[0].split()

        if not email_ids:
            print(f"No emails found with the subject: '{subject}'")
            return None

        # Get the latest email ID (IMAP returns them in ascending order)
        latest_email_id = email_ids[-1]
        print(
            f"Found {len(email_ids)} email(s). Fetching the latest one (ID: {latest_email_id.decode()})."
        )

        # Fetch the full email data (RFC822) for the latest ID
        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")

        if status != "OK":
            print("Failed to fetch email.")
            return None

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                # Parse the raw email data into a message object
                msg = email.message_from_bytes(response_part[1])

                # Initialize body
                email_body = ""
                email_datetime = parsedate_to_datetime(msg.get("Date", "Unknown Date"))

                # Walk through the email parts to find the body
                if msg.is_multipart():
                    # If it's multipart, iterate over the parts
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        # Look for the plain text part of the body
                        if (
                            content_type == "text/plain"
                            and "attachment" not in content_disposition
                        ):
                            try:
                                # Decode the payload and add it to the body
                                email_body = part.get_payload(decode=True).decode()
                                break  # Stop after finding the first plain text part
                            except Exception as e:
                                print(f"Could not decode part: {e}")
                else:
                    # If it's not multipart, the payload is the body
                    try:
                        email_body = msg.get_payload(decode=True).decode()
                    except Exception as e:
                        print(f"Could not decode payload: {e}")

                return email_body, email_datetime

    except imaplib.IMAP4.error as e:
        print(f"IMAP Error: {e}")
        print("Login failed. Please check your username and App Password.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    finally:
        # Always logout and close the connection
        if "mail" in locals() and mail.state == "SELECTED":
            mail.logout()
            print("Connection closed.")


# --- Main Execution ---
if __name__ == "__main__":
    notify2.init("Code")
    notification_title = "Teams Code"
    n = notify2.Notification(notification_title, "Checking for new emails...")
    n.set_urgency(notify2.URGENCY_NORMAL)
    n.show()
    body, email_datetime = get_latest_email_body_by_subject(
        USERNAME, IMAP_PASSWORD, IMAP_SERVER, SEARCH_SUBJECT
    )
    if body:
        match = re.search(r"Account verification code:\s*(\d+)\s", body)
        if match:
            code = match.group(1)
            pyclip.copy(code)
            n.update(
                notification_title,
                f"{email_datetime.astimezone().strftime('%a, %b %-d, %H:%M:%S')}: {code}",
            )
            n.set_urgency(notify2.URGENCY_NORMAL)
            n.set_timeout(10000)
            n.show()
        else:
            n.update(notification_title, "No code found in the email body.")
            n.set_urgency(notify2.URGENCY_NORMAL)
            n.set_timeout(2000)
            n.show()
