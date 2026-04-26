from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# --- Configurations ---
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-sporlyworks-key-replace-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 Day

app = FastAPI(title="SporlyWorks B2B API", version="1.0.0")

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# --- Mock Database ---
# In production, replace with an actual DB (e.g., PostgreSQL/Supabase)
MOCK_CLIENTS = {
    "admin@sporlyworks.com": {
        "email": "admin@sporlyworks.com",
        "hashed_password": pwd_context.hash("admin123"),
        "company": "SporlyWorks Admin",
        "tier": "enterprise"
    },
    "client@example.com": {
        "email": "client@example.com",
        "hashed_password": pwd_context.hash("client123"),
        "company": "Example Corp",
        "tier": "pro_suite"
    }
}

# --- Models ---
class Token(BaseModel):
    access_token: str
    token_type: str

class ClientData(BaseModel):
    email: str
    company: str
    tier: str

class WaitlistEntry(BaseModel):
    email: str
    company_name: str
    use_case: str
    selected_agent: str
    estimated_volume: str

# --- Auth Utils ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_client(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None or email not in MOCK_CLIENTS:
            raise credentials_exception
        return MOCK_CLIENTS[email]
    except JWTError:
        raise credentials_exception

# --- Endpoints ---

@app.post("/api/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    client = MOCK_CLIENTS.get(form_data.username)
    if not client or not verify_password(form_data.password, client["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": client["email"], "tier": client["tier"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/dashboard/status", response_model=ClientData)
async def get_client_dashboard(current_client: dict = Depends(get_current_client)):
    """Returns the dashboard data for the authenticated client."""
    return ClientData(
        email=current_client["email"],
        company=current_client["company"],
        tier=current_client["tier"]
    )

@app.post("/api/waitlist")
async def join_waitlist(entry: WaitlistEntry):
    """Endpoint for new businesses to join the autonomous workflow waitlist."""
    # In production, save to DB or trigger email to CEO via board_coordinator
    print(f"New waitlist entry: {entry.company_name} ({entry.email})")
    return {"status": "success", "message": "Added to waitlist"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "SporlyWorks B2B API"}
