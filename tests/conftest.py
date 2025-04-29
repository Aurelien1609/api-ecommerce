import os
import pytest
import dotenv
from sqlalchemy import event
from api_ecommerce.app import create_app
from api_ecommerce.config import SECRET_KEY

dotenv.load_dotenv()
DATABASE_SQL_TEST = os.getenv("DATABASE_SQL_TEST")


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config.update({"TESTING": True, "SECRET_KEY": SECRET_KEY})
    return app


@pytest.fixture()
def session(app):
    connection = app.session_factory.kw["bind"].connect()
    transaction = connection.begin()
    session = app.session_factory(bind=connection)
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        nonlocal nested
        if trans.nested and not trans._parent.nested:
            nested = connection.begin_nested()

    real_factory = app.session_factory
    app.session_factory = lambda: session

    yield session

    app.session_factory = real_factory  # Restore après test
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
