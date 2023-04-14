"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_all_users():
    all_users = User.query.all()
    all_users_serializable = list(map(lambda user: user.serialize(), all_users))
    return jsonify(all_users_serializable)

@app.route('/user', methods=['POST'])
def create_user():
    body = request.get_json()
    new_user = User(body['user_name'], body['email'], body['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"user": new_user.serialize()}), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    one_user = User.query.get(user_id)
    if one_user:
        return jsonify({"user": one_user.serialize()}), 200
    else:
        return jsonify({"msg": "Id not exist"})

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user_by_id(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "Deleted User"}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/people', methods=['GET'])
def get_people():
    all_people = People.query.all()
    all_people_serializable = list(map(lambda people: people.serialize(), all_people))
    return jsonify({"people": all_people_serializable})

@app.route('/people', methods=['POST'])
def create_people():
    body = request.get_json()
    new_people = People(body['name'], body['description'])
    db.session.add(new_people)
    db.session.commit()
    return jsonify({"people": new_people.serialize()})

@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_people(people_id):
    one_people = People.query.get(people_id)
    if one_people:
        return jsonify({"people": one_people.serialize()}), 200
    else:
        return jsonify({"msg": "Id not exist!"})

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_people(people_id):
    one_people = People.query.get(people_id)
    if one_people:
        db.session.delete(one_people)
        db.session.commit()
        return jsonify({"people": one_people.serialize()}), 200
    else:
        return jsonify({"error": "People not found"}), 404

@app.route('/planet', methods=['GET'])
def get_planet():
    all_planet = Planet.query.all()
    all_planet_serializable = list(map(lambda planet: planet.serialize(), all_planet))
    return jsonify({"planet": all_planet_serializable})

@app.route('/planet', methods=['POST'])
def create_planet():
    body = request.get_json()
    new_planet = Planet(body['name'], body['climate'])
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({"planet": new_planet.serialize()})

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    one_planet = Planet.query.get(planet_id)
    if one_planet:
        return jsonify({"planet": one_planet.serialize()}), 200
    else:
        return jsonify({"msg": "Id not exist!"})

@app.route('/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    one_planet = Planet.query.get(planet_id)
    if one_planet:
        db.session.delete(one_planet)
        db.session.commit()
        return jsonify({"planet": one_planet.serialize()}), 200
    else:
        return jsonify({"error": "Planet not found"}), 404

@app.route('/favorite', methods=['GET'])
def get_all_favorites():
    favorite = Favorite.query.all()
    serialized_favorite = [f.serialize() for f in favorite]
    return jsonify(serialized_favorite), 200

@app.route('/user/<int:user_id>/favorite', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"msg": "User not found."}), 404
    favorite = Favorite.query.filter_by(user_id=user_id).all()
    if not favorite:
        return jsonify({"msg": "No favorites found for the specified user."}), 404
    serialized_favorite = [f.serialize() for f in favorite]
    return jsonify({"favorite": serialized_favorite}), 200

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    body = request.get_json()
    user_id = body.get('user_id')
    if not user_id:
        return jsonify({"msg": "User ID is required."}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found."}), 404
    new_favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"favorite": new_favorite.serialize()}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    body = request.get_json()
    user_id = body.get('user_id')
    if not user_id:
        return jsonify({"msg": "User ID is required."}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found."}), 404
    new_favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({'favorite': new_favorite.serialize()}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.get_json().get('user_id')
    if not user_id:
        return jsonify({"msg": "User ID is required."}), 400
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"msg": "This planet is not in your favorites list."}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": favorite.serialize()}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = request.get_json().get('user_id')
    if not user_id:
        return jsonify({"msg": "User ID is required."}), 400
    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()
    if not favorite:
        return jsonify({"msg": "This people is not in your favorites list."}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": favorite.serialize()}), 200


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
