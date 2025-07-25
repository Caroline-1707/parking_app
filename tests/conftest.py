from datetime import datetime, timedelta

import pytest

from app import create_app
from config import TestingConfig
from models import Client, ClientParking, Parking, db


@pytest.fixture(scope="session")
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session


@pytest.fixture
def sample_client(db_session):
    client = Client(
        name="Ivan",
        surname="Ivanov",
        credit_card="1234567890123456",
        car_number="A123BC",
    )
    db_session.add(client)
    db_session.commit()
    return client


@pytest.fixture
def sample_parking(db_session):
    parking = Parking(
        address="123 Lenina St", opened=True, count_places=10, count_available_places=10
    )
    db_session.add(parking)
    db_session.commit()
    return parking


@pytest.fixture
def sample_client_parking(db_session, sample_client, sample_parking):
    client_parking = ClientParking(
        client_id=sample_client.id,
        parking_id=sample_parking.id,
        time_in=datetime.utcnow() - timedelta(hours=1),
    )
    sample_parking.count_available_places -= 1
    db_session.add(client_parking)
    db_session.commit()
    return client_parking
