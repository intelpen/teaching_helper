from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt

Base = declarative_base()
engine = create_engine("sqlite:///data/app.db")
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)


def init_auth_db():
    """Initialize the authentication database."""
    Base.metadata.create_all(engine)


def register_user(email, password):
    """Registers a new user with a hashed password."""
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(email=email, password_hash=password_hash)
    session.add(user)
    session.commit()


def authenticate_user(email, password):
    """Authenticates a user by verifying the email and password."""
    user = session.query(User).filter_by(email=email).first()
    if user and bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return True
    return False
