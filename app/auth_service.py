from fastapi import HTTPException, Depends
from datetime import datetime
import hashlib
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import SessionLocal
from model import UserTable

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def register_user(username: str, password: str, db: Session = Depends(get_db)):
    """Register a new user in the database."""
    # Check if user already exists
    existing_user = db.query(UserTable).filter(UserTable.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists.")
    
    # Create new user
    hashed_password = hash_password(password)
    new_user = UserTable(
        username=username,
        password_hash=hashed_password,
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully."}

def login_user(username: str, password: str, db: Session = Depends(get_db)):
    """Authenticate user and return token."""
    # Find user in database
    user = db.query(UserTable).filter(UserTable.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Verify password
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password.")
    
    # Return dummy token for demo (in production, use JWT)
    return {"token": f"fake-jwt-token-for-{username}", "username": username}
