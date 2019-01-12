from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DATETIME

Base = declarative_base()

class Login(Base):

    __tablename__ = 'ID_Login'
    
    uid = Column('column1', String(10), primary_key=True)
    loginDate = Column('column2', DATETIME, primary_key=True)

class ItemServer(Base):

    __tablename__ = 'ID_ItemID_Num_Server'

    uid = Column('UID', String, primary_key=True)
    date = Column('Date', DATETIME, primary_key=True)
    item_id = Column('ItemID', primary_key=True)
    item_num = Column('ItemNum', Integer)
    server = Column('ServerNo', String)

class Deposit(Base):
    __tablename__ = 'ID_Payment'
    
    uid = Column('UID', Integer, primary_key=True)
    trans_time = Column('TransTime', DATETIME, primary_key=True)
    deposit_amount = Column('DepositAmount', Integer)

# class Character(Base):
# 
#     __tablename__ = 'Character'

