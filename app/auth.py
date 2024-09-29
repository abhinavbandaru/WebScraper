from fastapi import Header, HTTPException

API_TOKEN = "my_secure_token"

async def verify_token(x_token: str = Header(...)):
    if x_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return x_token