from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


class User(db.Model):
    __tablename__ = 'users'  # , primaryjoin="users.c.id == components.c.user_id"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    components = db.relationship('Components', backref='user', lazy=True)

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
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    title = db.Column(db.String(50), nullable=True)
    image = db.Column(db.LargeBinary, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prices = db.relationship('Prices', backref='components', lazy=True)
    amounts = db.relationship('Amounts', backref='components', lazy=True)
    links = db.relationship('Links', backref='components', lazy=True)
    additional = db.relationship('Additional', backref='components', lazy=True)

    def __repr__(self):
        return str(self.__dict__)


class Prices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpu = db.Column(db.Integer, default=0)
    gpu = db.Column(db.Integer, default=0)
    motherboard = db.Column(db.Integer, default=0)
    ram = db.Column(db.Integer, default=0)
    case = db.Column(db.Integer, default=0)
    storage = db.Column(db.Integer, default=0)
    power_supply = db.Column(db.Integer, default=0)
    culler = db.Column(db.Integer, default=0)
    fan = db.Column(db.Integer, default=0)
    comp_id = db.Column(db.Integer, db.ForeignKey(
        'components.id'), nullable=False)

    def __repr__(self):
        return str(self.__dict__)


class Amounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpu = db.Column(db.Integer, default=0)
    gpu = db.Column(db.Integer, default=0)
    motherboard = db.Column(db.Integer, default=0)
    ram = db.Column(db.Integer, default=0)
    case = db.Column(db.Integer, default=0)
    storage = db.Column(db.Integer, default=0)
    power_supply = db.Column(db.Integer, default=0)
    culler = db.Column(db.Integer, default=0)
    fan = db.Column(db.Integer, default=0)
    comp_id = db.Column(db.Integer, db.ForeignKey(
        'components.id'), nullable=False)

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
    power_supply = db.Column(db.String(255), nullable=True)
    culler = db.Column(db.String(255), nullable=True)
    fan = db.Column(db.String(255), nullable=True)
    comp_id = db.Column(db.Integer, db.ForeignKey(
        'components.id'), nullable=False)

    def __repr__(self):
        return str(self.__dict__)


class Additional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comp = db.Column(db.String, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, default=0)
    amount = db.Column(db.Integer, default=1)
    link = db.Column(db.String(255), nullable=True)
    comp_id = db.Column(db.Integer, db.ForeignKey(
        'components.id'), nullable=False)

    def __repr__(self):
        return str(self.__dict__)
