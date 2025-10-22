# app/routes/jira_auth.py
import os
import requests
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse

router = APIRouter(prefix="/auth", tags=["Jira OAuth"])

CLIENT_ID = os.getenv("ATLASSIAN_CLIENT_ID")
CLIENT_SECRET = os.getenv("ATLASSIAN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/auth/callback"
SCOPES = "read:jira-user read:jira-work write:jira-work read:me"

AUTH_URL = (
    f"https://auth.atlassian.com/authorize?"
    f"audience=api.atlassian.com&client_id={CLIENT_ID}&scope={SCOPES}"
    f"&redirect_uri={REDIRECT_URI}&response_type=code&prompt=consent"
)

@router.get("/login")
async def login_to_jira():
    """Redirect user to Atlassian login."""
    return RedirectResponse(url=AUTH_URL)

@router.get("/callback")
async def jira_callback(request: Request, code: str):
    """Handle OAuth redirect and exchange code for access token."""
    token_url = "https://auth.atlassian.com/oauth/token"
    response = requests.post(
        token_url,
        json={
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
        headers={"Content-Type": "application/json"},
    )

    token_data = response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        # Redirect to frontend with error
        from urllib.parse import urlencode
        error_params = urlencode({"error": "Failed to authenticate with Jira"})
        return RedirectResponse(url=f"http://localhost:3000/?{error_params}")

    # Fetch accessible Jira sites
    res = requests.get(
        "https://api.atlassian.com/oauth/token/accessible-resources",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    sites = res.json()

    # Redirect to frontend with OAuth data
    from urllib.parse import urlencode
    import json
    params = urlencode({
        "access_token": access_token,
        "accessible_sites": json.dumps(sites)
    })
    return RedirectResponse(url=f"http://localhost:3000/?{params}")
