import datetime
import pandas
from sqlalchemy.orm import sessionmaker
from api_ecommerce.models import engine, User, Product

def build_database():

    session = sessionmaker(bind=engine)()

    admin_user = User(
        name="admin",
        email="admin@hotmail.com",
        password="password123",
        role="admin",
        date_creation=datetime.datetime(2010, 4, 1)

    )

    session.add(admin_user)
    session.commit()

    products = pandas.read_csv("../../data/raw_data/products.csv")
    for _, product in products.iterrows():
        new_product = Product(
            name = product.loc["Nom de produit"],
            description = product.loc["Description du produit"],
            category = product.loc["Catégorie du produit"],
            price = product.loc["Prix unitaire"],
            stock = product.loc["Quantité en stock"],
            date_creation = pandas.to_datetime(product.loc["Date d'ajout du produit"])
        )

        session.add(new_product)
    session.commit()
    session.close()
    print("DATABASE FILL SUCCESSFULLY")

if __name__ == "__main__":
    build_database()