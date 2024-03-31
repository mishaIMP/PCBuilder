from flask import Config


class SQLiteConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pc_builder.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BUNDLE_ERRORS = True
    SECRET_KEY = "3j4k5h43kj5hj234b5jh34bk25b5k234j5bk2j3b532"


class PostgresConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123@localhost:5432/pcbuilder'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    BUNDLE_ERRORS = True
    SECRET_KEY = "3j4k5h43kj5hj234b5jh34bk25b5k234j5bk2j3b532"
