from fastapi import FastAPI
from spinauth import router as spin_auth_router

app = FastAPI()

# Mount the spinauth endpoints (e.g., under /auth)
app.include_router(spin_auth_router, prefix="/auth")

# Now, POST requests to /auth/spin-auth will be handled by spinauth.
