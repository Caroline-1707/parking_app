from flask import Flask, request, jsonify
from datetime import datetime
from module_29_testing.hw.models import db, Client, Parking, ClientParking
from module_29_testing.hw.config import Config
from sqlalchemy.exc import IntegrityError


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['JSON_AS_ASCII'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/parkings', methods=['GET'])
    def get_parkings():
        parkings = Parking.query.all()
        return jsonify([{
            'id': p.id,
            'address': p.address,
            'opened': p.opened,
            'count_places': p.count_places,
            'count_available_places': p.count_available_places
        } for p in parkings])

    @app.route('/parkings/<int:parking_id>', methods=['GET'])
    def get_parking(parking_id):
        parking = Parking.query.get_or_404(parking_id)
        return jsonify({
            'id': parking.id,
            'address': parking.address,
            'opened': parking.opened,
            'count_places': parking.count_places,
            'count_available_places': parking.count_available_places
        })

    @app.route('/clients', methods=['GET'])
    def get_clients():
        clients = Client.query.all()
        return jsonify([{
            'id': client.id,
            'name': client.name,
            'surname': client.surname,
            'credit_card': client.credit_card,
            'car_number': client.car_number
        } for client in clients])

    @app.route('/clients/<int:client_id>', methods=['GET'])
    def get_client(client_id):
        client = Client.query.get_or_404(client_id)
        return jsonify({
            'id': client.id,
            'name': client.name,
            'surname': client.surname,
            'credit_card': client.credit_card,
            'car_number': client.car_number
        })

    @app.route('/clients', methods=['POST'])
    def create_client():
        try:
            data = request.get_json()
            if not data or 'name' not in data or 'surname' not in data:
                return jsonify({'message': 'Name and surname are required'}), 400
            client = Client(
                name=data['name'],
                surname=data['surname'],
                credit_card=data.get('credit_card'),
                car_number=data.get('car_number')
            )
            db.session.add(client)
            db.session.commit()
            return jsonify({'message': 'Client created', 'id': client.id}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'message': 'Error creating client'}), 400

    @app.route('/parkings', methods=['POST'])
    def create_parking():
        try:
            data = request.get_json()
            if not data or 'address' not in data or 'count_places' not in data:
                return jsonify({'message': 'Address and count_places are required'}), 400
            parking = Parking(
                address=data['address'],
                opened=data.get('opened', True),
                count_places=data['count_places'],
                count_available_places=data['count_places']
            )
            db.session.add(parking)
            db.session.commit()
            return jsonify({'message': 'Parking created', 'id': parking.id}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'message': 'Error creating parking'}), 400

    @app.route('/client_parkings', methods=['POST'])
    def enter_parking():
        try:
            data = request.get_json()
            if not data or 'client_id' not in data or 'parking_id' not in data:
                return jsonify({'message': 'client_id and parking_id are required'}), 400
            client = Client.query.get_or_404(data['client_id'])
            parking = Parking.query.get_or_404(data['parking_id'])
            if not parking.opened:
                return jsonify({'message': 'Parking is closed'}), 400
            if parking.count_available_places <= 0:
                return jsonify({'message': 'No available places'}), 400
            existing = ClientParking.query.filter_by(
                client_id=data['client_id'],
                parking_id=data['parking_id'],
                time_out=None
            ).first()
            if existing:
                return jsonify({'message': 'Client is already on this parking'}), 400
            client_parking = ClientParking(
                client_id=data['client_id'],
                parking_id=data['parking_id'],
                time_in=datetime.utcnow()
            )
            parking.count_available_places -= 1
            db.session.add(client_parking)
            db.session.commit()
            return jsonify({
                'message': 'Client entered parking',
                'time_in': client_parking.time_in.isoformat()
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'message': 'Error entering parking'}), 400

    @app.route('/client_parkings', methods=['DELETE'])
    def exit_parking():
        try:
            data = request.get_json()
            if not data or 'client_id' not in data or 'parking_id' not in data:
                return jsonify({'message': 'client_id and parking_id are required'}), 400
            client = Client.query.get_or_404(data['client_id'])
            parking = Parking.query.get_or_404(data['parking_id'])
            if not client.credit_card:
                return jsonify({'message': 'No credit card for payment'}), 400
            client_parking = ClientParking.query.filter_by(
                client_id=data['client_id'],
                parking_id=data['parking_id'],
                time_out=None
            ).first()
            if client_parking is None:
                return jsonify({'message': 'Client is not currently in this parking'}), 400
            time_out = datetime.utcnow()
            if time_out <= client_parking.time_in:
                return jsonify({'message': 'Time out cannot be earlier than time in'}), 400
            client_parking.time_out = time_out
            parking.count_available_places += 1
            db.session.commit()
            return jsonify({
                'message': 'Client exited parking',
                'time_in': client_parking.time_in.isoformat(),
                'time_out': client_parking.time_out.isoformat()
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({'message': 'Error exiting parking'}), 400

    return app
