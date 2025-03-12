from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Định nghĩa URL cho SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./survey.db"

# Tạo engine kết nối với SQLite
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Tạo session để làm việc với database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class để khai báo các model
Base = declarative_base()

