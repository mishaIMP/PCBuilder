from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_migrate import Migrate


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
    date = db.Column(db.Date, default=date.today())
    title = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    components = db.relationship('Components', backref='public_info', lazy=True, passive_deletes=True)
    additional_components = db.relationship('AdditionalComponents', backref='public_info', lazy=True, passive_deletes=True)
    
    def __repr__(self):
        return str(self.__dict__)


class Components(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component = db.Column(db.String, nullable=False)
    model = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, default=1)
    link = db.Column(db.String(255), nullable=True)
    public_info_id = db.Column(db.Integer, db.ForeignKey('public_info.id'), nullable=False)
    
    def __repr__(self):
        return str(self.__dict__)


class AdditionalComponents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component = db.Column(db.String, nullable=False)
    model = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, default=1)
    link = db.Column(db.String(255), nullable=True)
    public_info_id = db.Column(db.Integer, db.ForeignKey('public_info.id'), nullable=False)
    
    def __repr__(self):
        return str(self.__dict__)
