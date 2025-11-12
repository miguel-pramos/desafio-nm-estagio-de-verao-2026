from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from ..config.auth import JWT_ALG, JWT_EXP_MINUTES, UserDep, oauth
from ..config.db import SessionDep
from ..config.settings import SettingsDep
from ..repositories.auth import get_or_create_user
from ..schemas.auth import UserCreated
from ..utils.auth import create_jwt, delete_jwt_cookie, set_jwt_cookie

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/github/login")
async def github_login(request: Request):
    """Initiate GitHub OAuth login flow."""
    redirect_uri = request.url_for("github_callback")
    return await oauth.github.authorize_redirect(request, redirect_uri)


# @router.get("/github/callback", name="github_callback")
# async def github_callback(request: Request, settings: SettingsDep, session: SessionDep):
#     """Handle GitHub OAuth callback."""
#     token = await oauth.github.authorize_access_token(request)
#     resp = await oauth.github.get("user", token=token)
#     resp.raise_for_status()
#     user_info = resp.json()

#     user = get_or_create_user(session, user_info)
#     access_token = create_jwt(settings, str(user.id), JWT_ALG, JWT_EXP_MINUTES)

#     resp = RedirectResponse(url=settings.FRONTEND_URL)
#     set_jwt_cookie(resp, settings, access_token, JWT_EXP_MINUTES)
#     return resp


@router.get("/github/callback")
async def github_callback(request: Request, settings: SettingsDep, session: SessionDep):
    """Handle GitHub OAuth callback but redirect to frontend with token in querystring.

    This route does NOT set the cookie on the backend. Instead it redirects the
    user to the frontend page `/auth/set-cookie-client?token=...` which will
    persist the token as a cookie from the frontend server code.
    """
    token = await oauth.github.authorize_access_token(request)
    resp = await oauth.github.get("user", token=token)
    resp.raise_for_status()
    user_info = resp.json()

    user = get_or_create_user(session, user_info)
    access_token = create_jwt(settings, str(user.id), JWT_ALG, JWT_EXP_MINUTES)

    # Redirect to frontend route that will set the cookie on the client side
    redirect_url = f"{settings.FRONTEND_URL}/api/set-cookie-client?token={access_token}"
    return RedirectResponse(url=redirect_url)


@router.get("/logout")
async def logout(
    _session: SessionDep,
    settings: SettingsDep,
):
    """Logout user by clearing the JWT cookie."""
    resp = RedirectResponse(url=settings.FRONTEND_URL)
    delete_jwt_cookie(resp)
    return resp


@router.get("/me", response_model=UserCreated)
async def me(user: UserDep):
    assert user.id is not None
    return UserCreated(
        id=user.id, login=user.login, name=user.name, avatar_url=user.avatar_url
    )
