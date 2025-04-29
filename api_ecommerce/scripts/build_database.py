import datetime
import pandas
from sqlalchemy.orm import sessionmaker
from api_ecommerce.models import User, Product, Command, CommandLign, build_engine
from api_ecommerce.config import DATABASE_SQL
from werkzeug.security import generate_password_hash


def init_db():
    """
    Initialize and populate the database with default data.

    - Creates an administrator and a standard user.
    - Loads a list of products from a CSV file and inserts them into the database.
    - Adds a sample order for the standard user, including multiple order lines.

    Prerequisites:
        - Models User, Product, Command, and CommandLign are defined and imported.
        - The SQLAlchemy engine is initialized.
        - The function 'generate_password_hash' is imported.
        - The products CSV file is located at '../../data/raw_data/products.csv'.

    This function is intended for development and testing purposes.
    """
    session = sessionmaker(bind=build_engine(DATABASE_SQL)[0])()

    admin_user = User(
        name="admin",
        email="admin@hotmail.com",
        password=generate_password_hash("admin", method="pbkdf2:sha256"),
        role="admin",
        date_creation=datetime.datetime(2010, 4, 1),
    )
    session.add(admin_user)

    standard_user = User(
        name="john",
        email="john@hotmail.com",
        password=generate_password_hash("john123", method="pbkdf2:sha256"),
        role="user",
        date_creation=datetime.datetime(2014, 6, 1),
    )
    session.add(standard_user)
    session.commit()

    products = pandas.read_csv("data/raw_data/products.csv")
    for _, product in products.iterrows():
        new_product = Product(
            name=product.loc["Nom de produit"],
            description=product.loc["Description du produit"],
            category=product.loc["Catégorie du produit"],
            price=product.loc["Prix unitaire"],
            stock=product.loc["Quantité en stock"],
            date_creation=pandas.to_datetime(product.loc["Date d'ajout du produit"]),
        )

        session.add(new_product)
    session.commit()

    command = Command(
        user_id=standard_user.id,
        status="on hold",
        address_delivery="12 rue G.Brassens, 44000 Nantes",
        date_command=datetime.datetime.now(),
    )

    session.add(command)
    session.commit()

    command_lign_1 = CommandLign(
        product_id=1, command_id=command.id, quantity=2, price=1500
    )
    session.add(command_lign_1)

    command_lign_2 = CommandLign(
        product_id=2, command_id=command.id, quantity=5, price=200
    )
    session.add(command_lign_2)

    session.commit()

    session.close()
    print("✅ Database has been successfully initialized and populated.")


if __name__ == "__main__":
    init_db()
