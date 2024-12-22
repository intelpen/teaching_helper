from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///data/app.db")
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)  # "Student" or "Professor"


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)


class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    content = Column(Text)


def init_db():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
