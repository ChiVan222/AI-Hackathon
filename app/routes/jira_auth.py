# app/routes/jira_auth.py
import os
import requests
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
import json
# Ensure all these are imported:
from urllib.parse import urlencode, quote, urlparse, parse_qs, urlunparse, unquote

router = APIRouter(prefix="/auth", tags=["Jira OAuth"])

CLIENT_ID = os.getenv("ATLASSIAN_CLIENT_ID")
CLIENT_SECRET = os.getenv("ATLASSIAN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/auth/callback"
SCOPES = "read:jira-user read:jira-work write:jira-work read:me"

@router.get("/login")
async def login_to_jira(redirect_to: str = None):
    """
    Redirect user to Atlassian login, constructing the URL inside the function
    to ensure CLIENT_ID is loaded, and passing the frontend URL in 'state'.
    """
    BASE_AUTH_URL = (
        f"https://auth.atlassian.com/authorize?"
        f"audience=api.atlassian.com&client_id={CLIENT_ID}&scope={SCOPES}"
        f"&redirect_uri={REDIRECT_URI}&response_type=code&prompt=consent"
    )
    
    final_redirect_to = quote(redirect_to or "http://localhost:3000")
    
    final_auth_url = f"{BASE_AUTH_URL}&state={final_redirect_to}"
    
    return RedirectResponse(url=final_auth_url, status_code=status.HTTP_302_FOUND)

@router.get("/callback")
async def jira_callback(request: Request, code: str, state: str = None):
    """
    Handle OAuth redirect, exchange code for access token, and redirect 
    back to the original frontend URL using the 'state' parameter.
    """
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
    
    try:
        frontend_url = urlparse(unquote(state)).geturl() if state else "http://localhost:3000"
    except Exception:
        frontend_url = "http://localhost:3000"

    if not access_token:
        error_params = urlencode({"error": "Failed to authenticate with Jira"})
        return RedirectResponse(url=f"{frontend_url}?{error_params}")

    sites = [] 
    try:
        res = requests.get(
            "https://api.atlassian.com/oauth/token/accessible-resources",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    
        res.raise_for_status() 
        sites = res.json()
    except requests.RequestException:
        pass 

    encoded_sites = quote(json.dumps(sites))
    
    url_parts = urlparse(frontend_url)
    current_params = parse_qs(url_parts.query)
    
    current_params['access_token'] = [access_token]
    current_params['accessible_sites'] = [encoded_sites]
    
    new_query = urlencode(current_params, doseq=True)
    
    redirect_url = urlunparse(url_parts._replace(query=new_query, fragment='')) 
    
    # 4. Redirect to frontend with OAuth data
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)