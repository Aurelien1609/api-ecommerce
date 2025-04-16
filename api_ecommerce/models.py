from sqlalchemy import create_engine, Column, Integer, String, Float, DATETIME, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    date_creation = Column(DATETIME)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String)
    name = Column(String)
    role = Column(String, nullable=False)
    date_creation = Column(DATETIME)

    __table_args__ = (
        CheckConstraint(role.in_(["admin", "user"]), name="check_role"),
    )

engine = create_engine("sqlite:////Users/aurelien/Projects/blentai/api-ecommerce/data/db_data/ecommerce.db")
Base.metadata.create_all(engine)