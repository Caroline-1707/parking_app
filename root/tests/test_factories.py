from root.models import Client, Parking
from root.tests.factories import ClientFactory, ParkingFactory


def test_create_client_with_factory(client, db_session):
    client_data = ClientFactory.build()
    data = {
        "name": client_data.name,
        "surname": client_data.surname,
        "credit_card": client_data.credit_card,
        "car_number": client_data.car_number,
    }
    response = client.post("/clients", json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert "id" in resp_json
    client_obj = db_session.get(Client, resp_json["id"])
    assert client_obj is not None
    assert client_obj.name == data["name"]
    assert client_obj.surname == data["surname"]
    assert client_obj.credit_card == data["credit_card"]
    assert client_obj.car_number == data["car_number"]


def test_create_parking_with_factory(client, db_session):
    parking_data = ParkingFactory.build()
    data = {
        "address": parking_data.address,
        "opened": parking_data.opened,
        "count_places": parking_data.count_places,
    }
    response = client.post("/parkings", json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert "id" in resp_json
    parking = db_session.get(Parking, resp_json["id"])
    assert parking is not None
    assert parking.address == data["address"]
    assert parking.opened == data["opened"]
    assert parking.count_places == data["count_places"]
    assert parking.count_available_places == data["count_places"]
