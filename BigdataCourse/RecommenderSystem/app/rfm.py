# coding: utf-8
import sys
sys.path.append('/Users/hsnu130427/BigdataCourse/Recommender/')

import numpy as np
import pandas as pd
import datetime
from sqlalchemy import Column
from sqlalchemy.sql import select

from db_setting import db_connection
from db_setting import orm

class RFME():

    @classmethod
    def rfme_type(cls, user_id):
        conn = db_connection.engine.connect()

        return cls(conn, user_id)

    def __init__(self, conn, user_id):
        self.user_id = user_id
        self.deposit = pd.read_sql(select([orm.Deposit]).where(
            orm.Deposit.uid==user_id), conn)
        self.login = pd.read_sql(select([orm.Login]).where(
            orm.Login.uid==user_id), conn)

    def recency_type(self):
        
        user_latest = max(self.deposit.TransTime).date()
        global_latest = datetime.date(2018, 10, 10)
        diff = (global_latest - user_latest).days

        if diff > 300:
            recency = 'near'
        else:
            recency = 'far'
        return recency

    def frequency_type(self):
        
        first_deposit = min(self.deposit.TransTime) # first time to deposit
        last_deposit = max(self.deposit.TransTime) # last time to deposit
        
        deposit_diff = (last_deposit - first_deposit).days # how long between first and last
        deposit_count = sum(np.ones(self.deposit.shape[0])) # cashed how many times
        
        avgDep = deposit_count/deposit_diff # cash ___ times/ each day

        if avgDep >= 0.5:
            frequency = 'high'
        else:
            frequency = 'low'

        return frequency
    def monetary_type(self):
        
        if np.mean(self.deposit.DepositAmount.values) > 1000:
            monetary = 'high'
        else:
            monetary = 'low'
        return monetary

    def engagement_type(self):

        login_time = self.login.shape[0]
        oldest = min(self.login.column2) 
        latest = max(self.login.column2)

        try:
            avg_login = login_time / (latest-oldest).days

            if avg_login > 0.6:
                engagement = 'high'
            else:
                engagement = 'low'

        except:
            engagement = 'low' #only login 1 time
        
        return engagement


    def get_rfme_type(self):

        recency = self.recency_type()
        frequency = self.frequency_type()
        monetary = self.monetary_type()
        engagement = self.engagement_type()

        if recency == 'near':
            if frequency == 'high':
                if monetary == 'high':
                    if engagement == 'high':
                        rfme_type = '重要'
                    elif engagement == 'low':
                        rfme_type = '收集'
                elif monetary == 'low':
                    if engagement == 'high':
                        rfme_type = '潛力'
                    elif engagement == 'low':
                        rfme_type = '忙碌'                    
            elif frequency == 'low':
                if monetary == 'high':
                    if engagement == 'high':
                        rfme_type = '深耕'
                    elif engagement == 'low':
                        rfme_type = '土豪'
                elif monetary == 'low':
                    if engagement == 'high':
                        rfme_type = '一般玩家'
                    elif engagement == 'low':
                        rfme_type = '新人'  
        elif recency == 'far':
            if frequency == 'high':
                if monetary == 'high':
                    if engagement == 'high':
                        rfme_type = '喚回'
                    elif engagement == 'low':
                        rfme_type = '重點挽回'
                elif monetary == 'low':
                    if engagement == 'high':
                        rfme_type = '一般維持'
                    elif engagement == 'low':
                        rfme_type = '停滯'                    
            elif frequency == 'low':
                if monetary == 'high':
                    if engagement == 'high':
                        rfme_type = '活動型'
                    elif engagement == 'low':
                        rfme_type = '一般挽回'
                elif monetary == 'low':
                    if engagement == 'high':
                        rfme_type = '非課金'
                    elif engagement == 'low':
                        rfme_type = '路人'  

        return rfme_type

if __name__ == '__main__':

    common_user = pd.read_table('FourDatasetCommonUser.txt')
    common_user_list = common_user.values
    rfm_global = []
    count = 0
    for index, user in enumerate(common_user_list):
        user_id = int((user[0]).split(',')[1])
        rfm_global.append(RFME.rfme_type(user_id).get_rfme_type())
        
    rfm_global = pd.Series(rfm_global)
    # rfm_global.to_table('rfm_global.txt')
    print(rfm_global.value_counts())

    # print(RFME.rfme_type(3458960).get_rfme_type())