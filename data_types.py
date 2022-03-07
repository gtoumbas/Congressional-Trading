import uuid
from xmlrpc.client import Boolean
import zlib
import pickle
import sqlite3
from peewee import *
from playhouse import hybrid
# from sqlitedict import SqliteDict
# TODO might wanna switch to using peewee or django for database

database = SqliteDatabase("congress.db")

class BaseModel(Model):
    class Meta:
        database = database

class Member(BaseModel):

    name = CharField(unique=True, primary_key=True)
    party = CharField()
    state = CharField(default='NA')
    chamber = CharField()
    monthly_volume = FloatField(default=0.0)
    total_volume = FloatField(default=0.0)

    # TODO add more attributes i.e committees 

    # Calculated attributes TODO make this function

    # Might be complicated looking at pairs of buy sell and net winnings
    @hybrid.hybrid_property
    def win_perc(self):
        return 1.00
    


class Trade(BaseModel):

    event_id = AutoField()
    member = ForeignKeyField(Member, backref='trades')  
    num_shares = CharField()
    share_price = FloatField()
    stock = CharField()
    date = DateField()
    delay = IntegerField()
    kind = CharField(choices=[("buy", "sell"), ("buy", "sell")])  # Might wanna limit types with a dictionary
    done_by_family = BooleanField(default=False)    


def create_tables():
    with database:
        database.create_tables([Member, Trade])