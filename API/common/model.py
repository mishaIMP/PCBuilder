from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from sqlalchemy.orm import backref

db = SQLAlchemy()
migrate = Migrate()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    public_info = db.relationship('PublicInfo', backref='user', lazy=True, passive_deletes=True,
                                  cascade="all, delete-orphan")

    def __repr__(self):
        return str(self.__dict__)


class PublicInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    likes = db.Column(db.Integer, default=0)
    total_price = db.Column(db.Integer, nullable=True)
    author = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    components = db.relationship('Components', backref='public_info', lazy=True, passive_deletes=True,
                                 cascade="all, delete-orphan")

    def __repr__(self):
        return str(self.__dict__)


class Components(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpu = db.Column(db.String(75), nullable=True)
    gpu = db.Column(db.String(75), nullable=True)
    motherboard = db.Column(db.String(75), nullable=True)
    ram = db.Column(db.String(75), nullable=True)
    case = db.Column(db.String(75), nullable=True)
    storage = db.Column(db.String(75), nullable=True)
    psu = db.Column(db.String(255), nullable=True)
    culler = db.Column(db.String(75), nullable=True)
    fan = db.Column(db.String(75), nullable=True)
    public_info_id = db.Column(db.Integer, db.ForeignKey('public_info.id'), nullable=False)
    prices = db.relationship('Prices', backref='components', lazy=True, passive_deletes=True,
                             cascade="all, delete-orphan")
    amounts = db.relationship('Amounts', backref='components', lazy=True, passive_deletes=True,
                              cascade="all, delete-orphan")
    links = db.relationship('Links', backref='components', lazy=True, passive_deletes=True,
                            cascade="all, delete-orphan")
    additional = db.relationship('Additional', backref='components', lazy=True, passive_deletes=True,
                                 cascade="all, delete-orphan")

    def __repr__(self):
        return str(self.__dict__)


class Prices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpu = db.Column(db.Integer, nullable=True)
    gpu = db.Column(db.Integer, nullable=True)
    motherboard = db.Column(db.Integer, nullable=True)
    ram = db.Column(db.Integer, nullable=True)
    case = db.Column(db.Integer, nullable=True)
    storage = db.Column(db.Integer, nullable=True)
    psu = db.Column(db.Integer, nullable=True)
    culler = db.Column(db.Integer, nullable=True)
    fan = db.Column(db.Integer, nullable=True)
    comp_id = db.Column(db.Integer, db.ForeignKey('components.id'), nullable=False)

    def __repr__(self):
        return str(self.__dict__)


class Amounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpu = db.Column(db.Integer, nullable=True)
    gpu = db.Column(db.Integer, nullable=True)
    motherboard = db.Column(db.Integer, nullable=True)
    ram = db.Column(db.Integer, nullable=True)
    case = db.Column(db.Integer, nullable=True)
    storage = db.Column(db.Integer, nullable=True)
    psu = db.Column(db.Integer, nullable=True)
    culler = db.Column(db.Integer, nullable=True)
    fan = db.Column(db.Integer, nullable=True)
    comp_id = db.Column(db.Integer, db.ForeignKey('components.id'), nullable=False)

    def __repr__(self):
        return str(self.__dict__)


class Links(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpu = db.Column(db.String(255), nullable=True)
    gpu = db.Column(db.String(255), nullable=True)
    motherboard = db.Column(db.String(255), nullable=True)
    ram = db.Column(db.String(255), nullable=True)
    case = db.Column(db.String(255), nullable=True)
    storage = db.Column(db.String(255), nullable=True)
    psu = db.Column(db.String(255), nullable=True)
    culler = db.Column(db.String(255), nullable=True)
    fan = db.Column(db.String(255), nullable=True)
    comp_id = db.Column(db.Integer, db.ForeignKey('components.id'), nullable=False)

    def __repr__(self):
        return str(self.__dict__)


class Additional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comp = db.Column(db.String, nullable=False)
    model = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, default=1)
    link = db.Column(db.String(255), nullable=True)
    comp_id = db.Column(db.Integer, db.ForeignKey('components.id'), nullable=False)

    def __repr__(self):
        return str(self.__dict__)
