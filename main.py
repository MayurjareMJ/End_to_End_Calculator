### ✅ File: main.py (FastAPI Backend with SQLite and User Auth)
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, Float, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from passlib.context import CryptContext

app = FastAPI(title="FastAPI Calculator with Auth + DB")

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./calculations.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    calculations = relationship("Calculation", back_populates="owner")

class Calculation(Base):
    __tablename__ = "calculations"
    id = Column(Integer, primary_key=True, index=True)
    num1 = Column(Float)
    num2 = Column(Float)
    operation = Column(String)
    result = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="calculations")

Base.metadata.create_all(bind=engine)

# Auth logic
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
fake_tokens_db = {}

def get_user_by_username(db, username):
    return db.query(User).filter(User.username == username).first()

def fake_decode_token(token, db):
    if token not in fake_tokens_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    return db.query(User).filter(User.username == fake_tokens_db[token]).first()

# Schemas
class CalculationInput(BaseModel):
    num1: float
    num2: float
    operation: str

class UserCreate(BaseModel):
    username: str
    password: str

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = pwd_context.hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = f"{user.username}-token"
    fake_tokens_db[token] = user.username
    return {"access_token": token, "token_type": "bearer"}

@app.post("/calculate")
def calculate(data: CalculationInput, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = fake_decode_token(token, db)
    x, y = data.num1, data.num2
    op = data.operation.lower()

    if op == "add": result = x + y
    elif op == "subtract": result = x - y
    elif op == "multiply": result = x * y
    elif op == "divide": result = "Error: Division by zero" if y == 0 else x / y
    else: raise HTTPException(status_code=400, detail="Invalid operation")

    calc_entry = Calculation(
        num1=x,
        num2=y,
        operation=op,
        result=str(result),
        owner_id=user.id
    )
    db.add(calc_entry)
    db.commit()
    db.refresh(calc_entry)

    return {"result": result, "id": calc_entry.id}

@app.get("/history")
def history(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = fake_decode_token(token, db)
    records = db.query(Calculation).filter(Calculation.owner_id == user.id).all()
    return [{"num1": r.num1, "num2": r.num2, "operation": r.operation, "result": r.result} for r in records]
