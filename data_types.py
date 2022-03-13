import uuid
from venv import create
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
    party = CharField(default='NA')
    state = CharField(default='NA')
    district = CharField(default="NA")
    chamber = CharField()
    monthly_volume = FloatField(default=0.0)
    total_volume = FloatField(default=0.0)

    # TODO add more attributes i.e committees 

    # Calculated attributes TODO make this function

    # Might be complicated looking at pairs of buy sell and net winnings
    @hybrid.hybrid_property
    def win_perc(self):
        return 1.00

    def __str__(self):
        str = f"Name: {self.name}\nParty: {self.party}\n Chamber: {self.chamber}\n\
                state: {self.state}\district: {self.district}\n"
        return str


class Trade(BaseModel):

    event_id = AutoField()
    member = ForeignKeyField(Member, backref='trades')  
    asset_type = CharField(default="NA")
    high_amount = IntegerField()
    low_amount = IntegerField()
    share_price = FloatField(default="0.0")
    ticker = CharField()
    trade_date = DateField()
    disclosure_date = DateField()
    delay = IntegerField(default=-1)
    type = CharField()  # Might wanna limit types with a dictionary 
    owner = CharField()
    disclosure_url = CharField(default="NA")
    description = CharField(default="NA", null=True)

    def __str__(self):
        str = f"member: {self.member}\asset_type: {self.asset_type}\n high_amount: {self.high_amount}\n\
                low_amount: {self.low_amount}\ticker: {self.ticker}\n\
                trade_date: {self.trade_date}\type: {self.type}\n"
        return str

def create_tables():
    with database:
        database.create_tables([Member, Trade])

create_tables()