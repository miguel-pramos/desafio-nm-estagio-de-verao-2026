from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Response
from jose import JWTError, jwt

from ..config.settings import SettingsDep


def create_jwt(
    settings: SettingsDep,
    sub: str,
    alg: str,
    exp_minutes: int,
):
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=exp_minutes)

    payload = {
        "sub": sub,
        "iat": now,
        "exp": exp.timestamp(),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=alg)

    return token


def verify_jwt(settings: SettingsDep, token: str, alg: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[alg])
        return payload
    except JWTError:
        raise HTTPException(status_code=401)


def set_jwt_cookie(resp: Response, settings: SettingsDep, token: str, exp_minutes: int):
    # In production we need SameSite=None and Secure=True so the browser will
    # send the cookie on cross-site requests (frontend <-> backend on different
    # origins). In development keep Lax for easier local testing.
    secure = settings.ENV == "production"
    samesite = "none" if secure else "lax"

    resp.set_cookie(
        "access_token",
        token,
        httponly=True,
        secure=secure,
        samesite=samesite,
        max_age=exp_minutes * 60,
        path="/",
        domain=".vercel.app" if settings.ENV == "production" else None,
    )


def delete_jwt_cookie(resp: Response):
    resp.delete_cookie(
        "access_token",
        path="/",
    )
