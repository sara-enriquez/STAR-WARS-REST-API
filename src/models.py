from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80))
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __init__(self, user_name, email, password):
        self.user_name = user_name
        self.email = email
        self.password = password
        self.is_active = True

    def serialize(self):
        favorites_list = [f.serialize() for f in self.favorites]
        return {
            "id": self.id,
            "user_name": self.user_name,
            "email": self.email,
            "favorites": favorites_list
        }

class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(300), unique=False, nullable=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    climate = db.Column(db.String(80), unique=False, nullable=False)


    def __init__(self, name, climate):
        self.name = name
        self.climate = climate

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
        }

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    people_id = db.Column(db.Integer, db.ForeignKey('people.id')) 
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'))  
    
    user = db.relationship('User', backref='favorites') 
    planet = db.relationship('Planet', lazy='joined', backref='favorites')
    people = db.relationship('People', lazy='joined', backref='favorites')

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "people": self.people.serialize() if self.people else None, 
            "planet": self.planet.serialize() if self.planet else None 
        }