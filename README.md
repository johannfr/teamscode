# teamscode

Retrieves the latest sign-in code from MS-Teams via IMAP and stores it in the clipboard.

## Installation

Just `git clone`, do `uv sync` and then `uv run main.py`.

## Configuration

This script requires two environment variables, both of which can be read from a `.env` file:

```sh
IMAP_SERVER="imap.example.com"
IMAP_USERNAME="probably_your_email_address@example.com"
IMAP_PASSWORD="yourImapPassword"
```

### Using with Gmail

In order to use this with the GMail IMAP server, an "App Password" is required. This is different from your normal password and works more or less like an access-token. You need to search for "app password" while in the "Security" section of your account-settings.
