from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL="postgresql://postgres.hcfgpbknvppimqvswgjq:Deba9002043666@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require"

engine=create_engine(DATABASE_URL)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

def get_db():
 db=SessionLocal()
 try:
  yield db
 finally:
  db.close()

