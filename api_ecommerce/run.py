from api_ecommerce.app import create_app
from api_ecommerce.config import SECRET_KEY

app = create_app()

app.config["SECRET_KEY"] = SECRET_KEY

if __name__ == "__main__":
    app.run(debug=True)
