from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()

SUPABASE_URL = os.getenv("https://clpuzkgojwwtaycjbwyt.supabase.co")
SUPABASE_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNscHV6a2dvand3dGF5Y2pid3l0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUzODUzNTEsImV4cCI6MjA3MDk2MTM1MX0.u4BnBRfZfXTiA7Hlv6P-h5Gh3-C58qxZm8-df6MNVf0")

# Conexão com PostgreSQL do Supabase
engine = create_engine(f"postgresql+psycopg2://{SUPABASE_KEY}@{SUPABASE_URL}/postgres")

# Cria sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    return SessionLocal()