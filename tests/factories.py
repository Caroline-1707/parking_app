import factory
from models import Client, Parking


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    credit_card = factory.Faker("credit_card_number")
    car_number = factory.Faker("bothify", text="??###??")


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session_persistence = "commit"

    address = factory.Faker("address")
    opened = True
    count_places = 10
    count_available_places = 10
