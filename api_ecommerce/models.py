from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DATETIME,
    CheckConstraint,
    ForeignKey,
    Engine
)
from sqlalchemy.orm import declarative_base
from typing import Tuple, Optional

Base = declarative_base()


class Product(Base):
    """
    SQLAlchemy ORM model for a product in the ecommerce database.

    Attributes:
        id (int): Unique identifier for the product.
        name (str): Unique name of the product.
        description (str): Description of the product.
        category (str): Product category.
        price (float): Unit price of the product.
        stock (int): Quantity of product in stock.
        date_creation (datetime): Date the product was created.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    date_creation = Column(DATETIME)


class User(Base):
    """
    SQLAlchemy ORM model for a user.

    Attributes:
        id (int): Unique identifier for the user.
        email (str): Unique email address.
        password (str): Hashed password.
        name (str): Name of the user.
        role (str): Role of the user, can be 'admin' or 'user'.
        date_creation (datetime): Date the user was created.

    Constraints:
        - 'role' must be either 'admin' or 'user'.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String)
    role = Column(String, nullable=False, default="user")
    date_creation = Column(DATETIME)

    __table_args__ = (CheckConstraint(role.in_(["admin", "user"]), name="check_role"),)


class Command(Base):
    """
    SQLAlchemy ORM model for an order (command).

    Attributes:
        id (int): Unique identifier for the order.
        user_id (int): Foreign key referencing the user placing the order.
        status (str): Status of the order ('on hold', 'validated', 'canceled', 'shipped').
        address_delivery (str): Delivery address of the order.
        date_command (datetime): Date the order was placed.

    Constraints:
        - 'status' must be 'on hold', 'validated', 'canceled', or 'shipped'.
    """
    __tablename__ = "commands"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, nullable=False)
    address_delivery = Column(String, nullable=False)
    date_command = Column(DATETIME)

    __table_args__ = (
        CheckConstraint(
            status.in_(["on hold", "validated", "canceled", "shipped"]),
            name="check_status",
        ),
    )


class CommandLign(Base):
    """
    SQLAlchemy ORM model for an order line item.

    Attributes:
        id (int): Unique identifier for the line item.
        product_id (int): Foreign key referencing the product.
        command_id (int): Foreign key referencing the order.
        quantity (int): Quantity of the product in the order.
        price (int): Price of the product at the time of ordering.
    """
    __tablename__ = "commands_lign"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    command_id = Column(Integer, ForeignKey("commands.id"))
    quantity = Column(Integer, nullable=False, default=0)
    price = Column(Integer, nullable=False, default=0)


def build_engine(filename: str) -> Tuple[Engine, Optional[bool]]:
    """
    Create a SQLAlchemy engine instance connected to a SQLite database file,
    and initialize the database schema.

    Args:
        filename (str): The name of the SQLite database file (without extension).

    Returns:
        tuple: A tuple containing:
            - engine_instance: The SQLAlchemy engine connected to the SQLite database.
            - result: The result of Base.metadata.create_all(engine_instance).
    """
    engine_instance = create_engine(
        f"sqlite:///data/db_data/{filename}.db"
    )
    return engine_instance, Base.metadata.create_all(engine_instance)