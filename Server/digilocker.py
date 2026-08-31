import os
import base64
import hashlib
import hmac
import mimetypes
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests
from cryptography.fernet import Fernet

# DigiLocker / MeriPehchaan Requester production endpoints.
# Every endpoint can still be overridden from .env if API Setu gives GRSJ a
# partner-specific value during onboarding/go-live.
DEFAULT_BASE = "https://digilocker.meripehchaan.gov.in"
AUTHORIZE_URL = os.getenv("DIGILOCKER_AUTHORIZE_URL", f"{DEFAULT_BASE}/public/oauth2/1/authorize").strip()
TOKEN_URL = os.getenv("DIGILOCKER_TOKEN_URL", f"{DEFAULT_BASE}/public/oauth2/2/token").strip()
ISSUED_FILES_URL = os.getenv("DIGILOCKER_ISSUED_FILES_URL", f"{DEFAULT_BASE}/public/oauth2/2/files/issued").strip()
FILE_URI_URL = os.getenv("DIGILOCKER_FILE_URI_URL", f"{DEFAULT_BASE}/public/oauth2/1/file/uri").strip()
REVOKE_URL = os.getenv("DIGILOCKER_REVOKE_URL", f"{DEFAULT_BASE}/public/oauth2/1/revoke").strip()

DEFAULT_REDIRECT_URI = "https://hrms.grsj.in/admin/digilocker/callback"
DEFAULT_SCOPE = "files.issueddocs"


def client_id():
    return os.getenv("DIGILOCKER_CLIENT_ID", "").strip()


def client_secret():
    return os.getenv("DIGILOCKER_CLIENT_SECRET", "").strip()


def redirect_uri():
    return os.getenv("DIGILOCKER_REDIRECT_URI", DEFAULT_REDIRECT_URI).strip() or DEFAULT_REDIRECT_URI


def scope():
    return os.getenv("DIGILOCKER_SCOPE", DEFAULT_SCOPE).strip() or DEFAULT_SCOPE


def configured():
    # Callback has a production-safe default. Once client credentials are added,
    # HRMS is ready without any further code edits.
    return bool(client_id() and client_secret())


def configuration_status():
    missing=[]
    if not client_id(): missing.append("Client ID")
    if not client_secret(): missing.append("Client Secret")
    return {
        "configured": configured(),
        "missing": missing,
        "redirect_uri": redirect_uri(),
        "authorize_url": AUTHORIZE_URL,
        "token_url": TOKEN_URL,
        "issued_files_url": ISSUED_FILES_URL,
        "scope": scope(),
    }


def _fernet(secret_key):
    digest = hashlib.sha256(secret_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_token(value, secret_key):
    if not value:
        return None
    return _fernet(secret_key).encrypt(value.encode("utf-8")).decode("ascii")


def decrypt_token(value, secret_key):
    if not value:
        return None
    return _fernet(secret_key).decrypt(value.encode("ascii")).decode("utf-8")


def make_state():
    return secrets.token_urlsafe(48)


def make_pkce():
    verifier = secrets.token_urlsafe(64)[:96]
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    return verifier, challenge


def authorization_url(state, challenge):
    params = {
        "response_type": "code",
        "client_id": client_id(),
        "redirect_uri": redirect_uri(),
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "scope": scope(),
    }
    # Purpose is optional in DigiLocker, but communicates the exact GRSJ use-case
    # on consent screens where supported.
    purpose=os.getenv("DIGILOCKER_PURPOSE", "verification").strip()
    if purpose:
        params["purpose"] = purpose
    return AUTHORIZE_URL + "?" + urlencode(params)


def _response_error(response, default):
    try:
        payload=response.json()
        if isinstance(payload, dict):
            return payload.get("error_description") or payload.get("error") or default
    except Exception:
        pass
    text=(response.text or "").strip()
    return text[:500] if text else default


def exchange_code(code, verifier):
    response = requests.post(
        TOKEN_URL,
        data={
            "code": code,
            "grant_type": "authorization_code",
            "client_id": client_id(),
            "client_secret": client_secret(),
            "redirect_uri": redirect_uri(),
            "code_verifier": verifier,
        },
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(_response_error(response, f"DigiLocker token request failed ({response.status_code})."))
    payload=response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("DigiLocker token response was not valid JSON.")
    return payload


def list_issued_documents(access_token):
    response = requests.get(
        ISSUED_FILES_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(_response_error(response, f"Unable to list DigiLocker documents ({response.status_code})."))
    payload = response.json()
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("items", "files", "documents"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return []


def fetch_document(access_token, uri):
    response = requests.get(
        FILE_URI_URL,
        params={"uri": uri},
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=45,
    )
    if not response.ok:
        raise RuntimeError(_response_error(response, f"Unable to download DigiLocker document ({response.status_code})."))

    received_hmac = response.headers.get("hmac") or response.headers.get("HMAC")
    if received_hmac:
        digest = hmac.new(
            client_secret().encode("utf-8"),
            response.content,
            hashlib.sha256,
        ).digest()
        expected = base64.b64encode(digest).decode("ascii")
        if not hmac.compare_digest(expected.strip(), received_hmac.strip()):
            raise ValueError("DigiLocker document integrity verification failed (HMAC mismatch).")

    return response.content, response.headers.get("Content-Type", "application/octet-stream")


def revoke(access_token):
    if not access_token:
        return
    try:
        requests.post(
            REVOKE_URL,
            auth=(client_id(), client_secret()),
            data={"token": access_token},
            timeout=15,
        )
    except requests.RequestException:
        pass


def extension_for(content_type, fallback=".pdf"):
    ctype = (content_type or "").split(";")[0].strip().lower()
    mapping = {
        "application/pdf": ".pdf",
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "application/xml": ".xml",
        "text/xml": ".xml",
    }
    return mapping.get(ctype) or mimetypes.guess_extension(ctype) or fallback
