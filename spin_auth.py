# spin_auth.py

import os
import logging
import requests
from fastapi import APIRouter, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from jose import jwt, JWTError

logger = logging.getLogger(__name__)
router = APIRouter()

def get_dynamic_jwks_url(dynamic_env_id: str) -> str:
    """Return the JWKS URL for a given Dynamic environment ID."""
    return f"https://app.dynamic.xyz/api/v0/sdk/{dynamic_env_id}/.well-known/jwks"

def verify_dynamic_jwt(token: str, dynamic_env_id: str) -> dict:
    """
    Verify a JWT token using Dynamic's JWKS endpoint.
    
    Raises an exception if verification fails.
    """
    jwks_url = get_dynamic_jwks_url(dynamic_env_id)
    
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError as e:
        raise Exception("Error decoding token headers.") from e
    
    jwks = requests.get(jwks_url).json()
    key = None
    for k in jwks.get("keys", []):
        if k.get("kid") == unverified_header.get("kid"):
            key = k
            break
    if not key:
        raise Exception("Public key not found for token.")
    
    try:
        decoded = jwt.decode(token, key, algorithms=["RS256"], options={"verify_aud": False})
        return decoded
    except JWTError as e:
        raise Exception(f"JWT verification failed: {str(e)}") from e

@router.post("/auth")
async def spin_auth_endpoint(
    request: Request,
    authorization: str = Header(...)
):
    """
    Reusable authentication endpoint for Spin.
    
    Expects the Authorization header in the format: Bearer <token>
    """
    try:
        # Extract token from "Bearer <token>" header
        token = authorization.split(" ")[1]
        token = token.strip('"')
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format.")
    
    token_parts = token.split(".")
    logger.info("Received token parts: %s", token_parts)
    if len(token_parts) != 3:
        raise HTTPException(status_code=401, detail="Provided token is not in a valid JWT format.")
    
    dynamic_env_id = os.getenv("DYNAMIC_ENV_ID")
    if not dynamic_env_id:
        raise HTTPException(status_code=500, detail="Server configuration error: DYNAMIC_ENV_ID not set.")
    
    try:
        decoded_token = verify_dynamic_jwt(token, dynamic_env_id)
    except Exception as e:
        logger.error("JWT verification failed. Token parts: %s. Error: %s", token_parts, str(e))
        raise HTTPException(status_code=401, detail=f"JWT verification failed: {str(e)}")
    
    body = await request.json()
    user_data = body.get("user", {})
    
    return JSONResponse(content={
        "message": "User authenticated successfully",
        "user": user_data,
        "claims": decoded_token
    })
