import sys
sys.path.append('/Users/hsnu130427/BigdataCourse/Recommender/')

import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy.sql import select

from db_setting import db_connection
from db_setting import data_config
from db_setting import orm

conn = db_connection.engine.connect()

''' Deposit Record
'''

class TimePayment():

    def get_data(self):

        df = pd.read_sql(select([orm.Deposit]), conn)
        df.columns = data_config.TIME_PAYMENT_COLUMNS
        df['Weekday'] = df.TransTime.apply(lambda x: x.weekday())

        return df

''' Character Feature: 819375 female and 1135955 male
'''
character = pd.read_table(data_config.CHARACTER_PATH).iloc[21:,:]
# time_payment = pd.read_sql(select([orm.Deposit]), conn)
character.columns = data_config.CHARACTER_COLUMNS

''' Login
'''
class Login():

    def get_data(self):

        df = pd.read_sql(select([orm.Login]), conn)
        df.columns = data_config.LOGIN_COLUMNS
        df['LoginTime'] = [1]*(df.shape[0])
        df['Weekday'] = df.LoginDate.apply(lambda x: x.weekday())

        return df

''' Item User Record
'''
class ItemServer():
    
    def get_data(self):

        # if item_id == None:
        # df = pd.read_sql(select([orm.ItemServer]), conn)
        # else:
        #     df = pd.read_sql(select([orm.ItemServer]).where(
        #         orm.ItemServer.item_id==item_id), conn)
        df = pd.read_table(data_config.ITEM_SERVER_PATH)
        df.columns = data_config.ITEM_SERVER_COLUMNS

        item_type = pd.read_table(data_config.ITEM_TYPE_PATH)
        item_set = pd.read_table(data_config.ITEM_SET_PATH)
        item_type = item_type.set_index('ItemID').to_dict()['ItemType']
        item_set = item_set.set_index('ItemID').to_dict()['SetType']

        df['ItemType'] = df.iloc[:, 2].apply(lambda x: item_type.get(x))
        df['SetType'] = df.iloc[:, 2].apply(lambda x: item_set.get(x))

        return df

''' Association Rules
'''
class Association():

    def data_to_list(self, str_list):
        split_set = str_list.split(',')
        # list_data = []
        if len(split_set) == 2:
            list_data = [split_set[0][1:], split_set[1][:-1]]
        else:
            list_data = [code for code in split_set[1:-1]]
            list_data.append(split_set[0][1:])
            list_data.append(split_set[1][:-1])
        
        list_data = [int(code) for code in list_data]

        return list_data

    def get_data(self):

        df = pd.read_csv(data_config.ASSOCIATION_PATH).iloc[:,1:]
        df.ItemSet = df.ItemSet.apply(self.data_to_list)

        return df

if __name__ == '__main__':

    # print(time_payment.head())
    # print(character.head())
    # print(login.head())
    # print(item_server.head())

    login = Login()
    login = login.get_data()
    print(login.head)