from playhouse.sqlite_ext import SqliteDatabase
from peewee import Model, TextField, CharField

db = SqliteDatabase('nitro.db')


class User(Model):
    id = CharField(18, primary_key=True)
    nitro_name = TextField(unique=True)

    class Meta:
        db_table = 'users'
        database = db
