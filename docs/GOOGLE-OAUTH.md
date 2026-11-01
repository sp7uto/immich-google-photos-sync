# Google Photos OAuth

This project uses the `https://www.googleapis.com/auth/photoslibrary.appendonly` scope to upload new media to Google Photos.

## Set up a Google Cloud project

1. Create or select a project in Google Cloud Console.
2. Enable the Google Photos Library API.
3. Configure the OAuth consent screen according to Google's current requirements.
4. Create an **OAuth desktop application** client.
5. Download the client JSON as `credentials.json`.

Google's verification, testing-user and production requirements can change; consult the current Google Cloud documentation.

## Authorize on a computer with a browser

Run this step **on a trusted desktop**, not in the headless container:

```bash
python -m venv .venv
. .venv/bin/activate
pip install google-auth-oauthlib
python get_google_token.py
```

Place `credentials.json` beside the helper while authorizing. The helper opens a local browser and writes `token.json`.

Copy **both** JSON files to the private `data/` directory used by Docker Compose. Never commit them.

## Notes

- Google Photos may restrict what apps can read or manage; this application only uploads.
- A refresh token can be revoked by the user or Google.
- The panel has no built-in OAuth login page.
- Successful uploads go to the library, not to a specified Google album.
