"""
get_oauth_token.py — OAuth2 refresh-token helper for MindStack LMS.

Gets a Gmail OAuth2 refresh token using the Google OAuth2 flow.
Run once from the terminal to obtain a refresh token, then store it
in config.py if you want to use OAuth2 instead of an App Password.

Requirements:
    pip install google-auth-oauthlib

Usage:
    python get_oauth_token.py --client-id YOUR_ID --client-secret YOUR_SECRET

The script will open your browser for consent and then print the
refresh token to the terminal.
"""

import argparse
import sys

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print(
        "google-auth-oauthlib is not installed.\n"
        "Install it with:  pip install google-auth-oauthlib"
    )
    sys.exit(1)

GMAIL_SEND_SCOPE = ["https://mail.google.com/"]


def get_gmail_refresh_token(client_id: str, client_secret: str) -> str:
    """Run the OAuth2 installed-app flow and return the refresh token."""
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=GMAIL_SEND_SCOPE)
    # Opens a local browser tab for consent; falls back to manual URL copy.
    credentials = flow.run_local_server(port=0, prompt="consent", access_type="offline")

    return credentials.refresh_token


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Obtain a Gmail OAuth2 refresh token for use with MindStack LMS mailer."
    )
    parser.add_argument("--client-id",     required=True, help="Google OAuth2 client ID")
    parser.add_argument("--client-secret", required=True, help="Google OAuth2 client secret")
    args = parser.parse_args()

    print("\nOpening browser for Google consent…\n")
    token = get_gmail_refresh_token(args.client_id, args.client_secret)

    print("\n" + "=" * 60)
    print("Refresh Token:")
    print(token)
    print("=" * 60)
    print("\nAdd this token to mail/config.py under smtp.refresh_token.")
    print("Then switch smtp.auth_method to 'oauth2'.\n")


if __name__ == "__main__":
    main()
