from datetime import UTC, datetime, timedelta
import os
from urllib.parse import urlencode

import requests

GOOGLE_OAUTH_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_API_URL = "https://www.googleapis.com/calendar/v3"
GOOGLE_CALENDAR_SCOPE = os.getenv("GOOGLE_CALENDAR_SCOPE", "https://www.googleapis.com/auth/calendar")


def _google_client_id() -> str:
    return os.getenv("GOOGLE_CLIENT_ID", "")


def _google_client_secret() -> str:
    return os.getenv("GOOGLE_CLIENT_SECRET", "")


def _google_redirect_uri() -> str:
    return os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:8000/api/v1/integracoes/google/callback")


def build_google_consent_url(state_token: str) -> str:
    params = {
        "client_id": _google_client_id(),
        "redirect_uri": _google_redirect_uri(),
        "response_type": "code",
        "scope": GOOGLE_CALENDAR_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": state_token,
    }
    return f"{GOOGLE_OAUTH_AUTH_URL}?{urlencode(params)}"


def exchange_code_for_token(code: str) -> dict:
    response = requests.post(
        GOOGLE_OAUTH_TOKEN_URL,
        data={
            "code": code,
            "client_id": _google_client_id(),
            "client_secret": _google_client_secret(),
            "redirect_uri": _google_redirect_uri(),
            "grant_type": "authorization_code",
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def refresh_access_token(refresh_token: str) -> dict:
    response = requests.post(
        GOOGLE_OAUTH_TOKEN_URL,
        data={
            "client_id": _google_client_id(),
            "client_secret": _google_client_secret(),
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    if "refresh_token" not in data:
        data["refresh_token"] = refresh_token
    return data


def token_expiration(expires_in_seconds: int | None) -> datetime | None:
    if not expires_in_seconds:
        return None
    return datetime.now(UTC) + timedelta(seconds=int(expires_in_seconds))


def fetch_google_profile(access_token: str) -> dict:
    response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def list_busy_slots(
    access_token: str,
    *,
    calendar_id: str,
    time_min_iso: str,
    time_max_iso: str,
) -> list[dict]:
    response = requests.get(
        f"{GOOGLE_CALENDAR_API_URL}/calendars/{calendar_id}/events",
        params={
            "timeMin": time_min_iso,
            "timeMax": time_max_iso,
            "singleEvents": "true",
            "orderBy": "startTime",
        },
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20,
    )
    response.raise_for_status()
    items = response.json().get("items", [])
    slots: list[dict] = []
    for item in items:
        start = item.get("start", {}).get("dateTime") or item.get("start", {}).get("date")
        end = item.get("end", {}).get("dateTime") or item.get("end", {}).get("date")
        slots.append(
            {
                "google_event_id": item.get("id"),
                "titulo": item.get("summary"),
                "inicio": start,
                "fim": end,
            }
        )
    return slots


def create_google_event(
    access_token: str,
    *,
    calendar_id: str,
    titulo: str,
    descricao: str | None,
    inicio_iso: str,
    fim_iso: str,
) -> dict:
    response = requests.post(
        f"{GOOGLE_CALENDAR_API_URL}/calendars/{calendar_id}/events",
        json={
            "summary": titulo,
            "description": descricao,
            "start": {"dateTime": inicio_iso},
            "end": {"dateTime": fim_iso},
        },
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def update_google_event(
    access_token: str,
    *,
    calendar_id: str,
    google_event_id: str,
    titulo: str,
    descricao: str | None,
    inicio_iso: str,
    fim_iso: str,
) -> dict:
    response = requests.patch(
        f"{GOOGLE_CALENDAR_API_URL}/calendars/{calendar_id}/events/{google_event_id}",
        json={
            "summary": titulo,
            "description": descricao,
            "start": {"dateTime": inicio_iso},
            "end": {"dateTime": fim_iso},
        },
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def delete_google_event(access_token: str, *, calendar_id: str, google_event_id: str) -> None:
    response = requests.delete(
        f"{GOOGLE_CALENDAR_API_URL}/calendars/{calendar_id}/events/{google_event_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20,
    )
    response.raise_for_status()
