import pytest
from module_29_testing.hw.models import Client, Parking, ClientParking
from datetime import datetime, timedelta


@pytest.mark.parametrize("route", [
    '/clients',
    '/clients/1',
    '/parkings',
    '/parkings/1',
])
def test_get_methods(client, sample_client, sample_parking, route):
    response = client.get(route)
    assert response.status_code == 200


def test_get_nonexistent_client(client):
    response = client.get('/clients/999')
    assert response.status_code == 404


def test_get_nonexistent_parking(client):
    response = client.get('/parkings/999')
    assert response.status_code == 404


def test_create_client(client, db_session):
    data = {
        'name': 'Name',
        'surname': 'Surname',
        'credit_card': '9876543210987654',
        'car_number': 'B456CD'
    }
    response = client.post('/clients', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert 'id' in resp_json
    client_obj = db_session.get(Client, resp_json['id'])
    assert client_obj is not None
    assert client_obj.name == 'Name'
    assert client_obj.surname == 'Surname'
    assert client_obj.credit_card == data['credit_card']
    assert client_obj.car_number == data['car_number']


def test_create_parking(client, db_session):
    data = {
        'address': '456 Street St',
        'opened': True,
        'count_places': 20
    }
    response = client.post('/parkings', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert 'id' in resp_json
    parking = db_session.get(Parking, resp_json['id'])
    assert parking is not None
    assert parking.address == '456 Street St'
    assert parking.opened is True
    assert parking.count_places == 20
    assert parking.count_available_places == 20


@pytest.mark.parking
def test_enter_parking(client, sample_client, sample_parking, db_session):
    old_available = sample_parking.count_available_places
    data = {
        'client_id': sample_client.id,
        'parking_id': sample_parking.id
    }
    response = client.post('/client_parkings', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert 'time_in' in resp_json

    parking = db_session.get(Parking, sample_parking.id)
    assert parking.count_available_places == old_available - 1

    client_parking = db_session.query(ClientParking).filter_by(
        client_id=sample_client.id,
        parking_id=sample_parking.id,
        time_out=None
    ).first()
    assert client_parking is not None
    assert client_parking.time_in is not None


@pytest.mark.parking
def test_exit_parking(client, sample_client, sample_parking, sample_client_parking, db_session):
    data = {
        'client_id': sample_client.id,
        'parking_id': sample_parking.id
    }
    response = client.delete('/client_parkings', json=data)
    assert response.status_code == 200
    resp_json = response.get_json()
    assert 'time_in' in resp_json
    assert 'time_out' in resp_json
    parking = db_session.get(Parking, sample_parking.id)
    assert parking.count_available_places == sample_parking.count_available_places
    client_parking = db_session.get(ClientParking, sample_client_parking.id)
    assert client_parking.time_out is not None
    assert client_parking.time_out > client_parking.time_in


def test_enter_closed_parking(client, sample_client, db_session):
    parking = Parking(
        address='789 Street St',
        opened=False,
        count_places=5,
        count_available_places=5
    )
    db_session.add(parking)
    db_session.commit()
    data = {
        'client_id': sample_client.id,
        'parking_id': parking.id
    }
    response = client.post('/client_parkings', json=data)
    assert response.status_code == 400
    assert 'closed' in response.get_json()['message'].lower()


def test_exit_without_card(client, db_session):
    client_no_card = Client(
        name='NoCard',
        surname='User',
        car_number='X999XX'
    )
    db_session.add(client_no_card)
    parking = Parking(
        address='101 Street St',
        opened=True,
        count_places=3,
        count_available_places=2
    )
    db_session.add(parking)
    db_session.commit()
    client_parking = ClientParking(
        client_id=client_no_card.id,
        parking_id=parking.id,
        time_in=datetime.utcnow() - timedelta(hours=1)
    )
    db_session.add(client_parking)
    db_session.commit()
    data = {
        'client_id': client_no_card.id,
        'parking_id': parking.id
    }
    response = client.delete('/client_parkings', json=data)
    assert response.status_code == 400
    assert 'credit card' in response.get_json()['message'].lower()
