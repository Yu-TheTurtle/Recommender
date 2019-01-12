import logging

import numpy as np
import pandas as pd
from scipy import sparse
from lightfm import LightFM
from lightfm.evaluation import precision_at_k
from lightfm.evaluation import auc_score
from sqlalchemy.sql import select
from mlxtend.frequent_patterns import apriori
import mpld3

# from db_setting.db_connection import session_scope
from db_setting import data_resource
from db_setting import orm
from app import user_recommend
from app import rfm

class user_outcome():

    def __init__(self, user_info, rfm, item, friend, partner):
        self.user_info = user_info
        self.rfm = rfm
        self.item = item
        self.friend = friend
        self.partner = partner

class item_outcome():

    def __init__(self, basic_info, server_stat,baskset_pair, basket_set,top_customer):
        self.basic_info = basic_info
        self.server_stat = server_stat
        self.baskset_pair = baskset_pair
        self.baskset_set = basket_set
        self.top_customer = top_customer

# class item_outcome()
class Recommender():

    def __init__(self):
        self.pivot = None
        self.item_server = None
        self.conn = data_resource.conn

    ''' For user recommendation
    '''
    def build_pivot(self):

        item_server = data_resource.ItemServer()
        self.item_server = item_server.get_data()
        pivot = self.item_server.pivot_table(index='UID', columns='ItemID', values='ItemNum')
        logging.info('Finish building pivot table for item and user')

        return pivot
 
    def get_item_user_pivot(self):
        
        # build pivot table with data from db and fill in 0 for NaN
        item_pivot_df = self.build_pivot().fillna(0)
        
        self.pivot = item_pivot_df
        # transfer inro coo matrix
        train_data = sparse.csr_matrix(item_pivot_df.values)
        
        return train_data

    def train_model(self, recom_target, no_components=30, loss='warp', epochs=50):
        ''' intialize at the first time user login into the system
        '''
        if recom_target == 'user':
            train = self.get_item_user_pivot()
        elif recom_target == 'item':
            train = np.transpose(self.get_item_user_pivot())

        if train.shape[0] != 0:
            model = LightFM(no_components=30, loss='warp')
            logging.info('Start to train recommend model.')
            model.fit(train, epochs=50)
            prediction = precision_at_k(model, train, k=5)      
            train_auc = auc_score(model, train).mean()
            logging.info('Finish training with precision {} and AUC {}'.format(prediction.mean(), train_auc))
        else:
            model = None
            logging.info('Data type wrong with type {}'.format(type(train)))
        
        # self.model = model
        return model

    def get_top_n_items_recommend(self, user_id, n):
        ''' recommend based on given user_id
        '''
        model = self.train_model(recom_target='user')
        print(self.pivot)
        # self.pivot = pivot
        code_df = pd.DataFrame({'Loc':range(self.pivot.shape[0]),'UID':self.pivot.index})
        # print('User Code DF')
        # print(code_df)
        user_loc = code_df.loc[code_df.UID == user_id].Loc.values[0]
        
        predict = model.predict(item_ids=list(range(self.pivot.shape[1])),
                                user_ids=[user_loc])
        predict_df = pd.DataFrame({'Loc': range(self.pivot.shape[1]), 'Value': predict})
        topn_loc = predict_df.sort_values('Value', ascending=False).Loc[:n].tolist()

        top_n = list(self.pivot.columns[topn_loc])
        
        ######
        top_n_item = []
        df = data_resource.ItemServer()
        df = df.get_data()

        for item in top_n:

            item_df = df.loc[df.ItemID == item]
            purchase_record = sum(item_df.ItemNum)
            if item_df.shape[0] > 1:
                item_df = item_df.sample(n=1)
            top_n_item.append([item, item_df.ItemType.values[0], purchase_record])

        ######
        return top_n_item

    def get_rfm_category(self, user_id):

        rfm_category = rfm.RFME.rfme_type(user_id).get_rfme_type()

        return rfm_category 

    def get_user_resp(self, user_id):

        print('Start to get social recommend')
        social_recommend = user_recommend.UserRecommender()
        user_info, friend, partner = social_recommend.get_friend_partner_recommend(user_id)

        print(user_info)
        print(partner)
        print('user_info')
        print('Start to get top n recommend item and rfm type')

        resp = user_outcome(
                user_info = user_info,
                rfm = self.get_rfm_category(user_id),
                item= self.get_top_n_items_recommend(user_id, 5),
                friend= friend,
                partner= partner
        )

        return resp
    
    ''' For Item data
    '''
    
    def get_top_n_users_recommend(self, item_id, n):

        model = self.train_model(recom_target='item')

        code_df = pd.DataFrame({'Loc':range(self.pivot.shape[1]),
                'UID': pd.Series(self.pivot.columns).apply(lambda x: int(x))})
        item_loc = code_df.loc[code_df.UID == item_id].Loc.values[0]

        predict = model.predict(item_ids=list(range(self.pivot.shape[0])),
                                user_ids=[item_loc])
        
        predict_df = pd.DataFrame({'Loc': range(self.pivot.shape[0]), 'Value': predict})
        top5_loc = predict_df.sort_values('Value', ascending=False).Loc[:n].tolist()

        top_5_user = list(self.pivot.index[top5_loc])

        return top_5_user

    def get_item_basket(self, item_id):

        # intialize item_server for computing server stat
        item_server = data_resource.ItemServer()
        self.item_server = item_server.get_data()

        assc = data_resource.Association()
        assco_df = assc.get_data()
        tar_df = assco_df.loc[assco_df.ItemSet.apply(lambda x: item_id in x)]

        paired_df = (tar_df.loc[tar_df.ItemSet.apply(lambda x: len(x) == 2)]).sort_values(
                        ['Confidence'], ascending=False).iloc[:5,:]
        set_df =  (tar_df.loc[tar_df.ItemSet.apply(lambda x: len(x) > 2)]).sort_values(
                        ['Confidence'], ascending=False).iloc[:5,:]

        pair_list, set_list = [], []

        for index, entry in paired_df.iterrows():
            item_set = [x for x in entry.ItemSet if x != item_id]
            pair_list.append([item_set[0], int(entry.Support * 153081), entry.Confidence])

        for index, entry in set_df.iterrows():
            item_set = [str(x) for x in entry.ItemSet if x != item_id]
            item_set_str = ', '.join(item_set)
            set_list.append([item_set_str, int(entry.Support * 153081), entry.Confidence])

        return pair_list, set_list

    def get_top_customer(self, item_id):

        # df = pd.read_sql(select([orm.ItemServer]).where(orm.ItemServer.item_id == item_id), data_resource.conn)
        # print(df)
        # item_server = data_resource.ItemServer()
        # df = item_server.get_data()
        df = self.item_server
        df = df.loc[df.ItemID == item_id]
        # print(df)
        item_cate = df.ItemType.iloc[0]

        top_df = (df.groupby('UID').agg('sum')).sort_values('ItemNum', ascending=False).iloc[:5,:]
        # print(top_df)
        top_customer = []
        for index, entry in top_df.iterrows():
            top_customer.append([index, entry.ItemNum]) # customer_id & bought amount

        return item_cate, top_customer

    def get_item_resp(self, item_id):

        pair_list, set_list = self.get_item_basket(item_id)
        item_cate, top_customer = self.get_top_customer(item_id)

        item_stat = pd.read_csv('precomputed_data/item_server_statistics.csv')
        item_stat.index = item_stat.ItemID
        tar_df = item_stat.loc[item_stat.ItemID == item_id]

        ''' Basic data
        '''
        pur_rec = tar_df.PurRec.values[0]
        top_server = tar_df.iloc[:, 1:-1].idxmax(axis=1).values[0][-1]
        purchase_rank_serie = (item_stat.PurRec.rank(ascending=False).apply(lambda x: int(x)))
        rank = purchase_rank_serie.loc[purchase_rank_serie.index == item_id].values[0]
        global_rank = str(rank) + '/' + str(len(item_stat))
        basic_info = [item_cate, top_server, pur_rec, global_rank]

        ''' Stat based on different server
        '''
        # item rank for each server
        server_rank = []
        for name, column in item_stat.iloc[:,1:-1].iteritems(): # only server1~4
            rank_serie = column.rank(ascending=False).apply(lambda x: int(x))
            rank = rank_serie.loc[rank_serie.index == item_id].values[0]
            rank = str(rank) + '/' + str(len(item_stat))
            server_rank.append(rank)
        server_rank.append(global_rank)

        sales_rate = (self.item_server.loc[self.item_server.ItemID==item_id].groupby(
                                    ['ItemID','RecordTime', 'ServerNo']).agg('sum').unstack().iloc[:, -4:])
        server_stat = list(sales_rate.iloc[-1,:].values)
        server_stat.append(sum(server_stat))
        sales_rate = list(sales_rate.iloc[-2:,:].apply(lambda x: ((x[1] - x[0])/x[0])*100))
        sales_rate.append(sum(sales_rate) / 4)
        sales_rate = [str(round(rate, 2)) + '%' for rate in sales_rate]

        server_total_stat = []
        for i in range(5):
            server_total_stat.append([server_stat[i], sales_rate[i], server_rank[i]])
        # server_total_stat = [server_stat, server_rank, sales_rate]

        resp = item_outcome(
            basic_info=basic_info,
            server_stat=server_total_stat, 
            baskset_pair=pair_list, 
            basket_set=set_list,
            top_customer=top_customer
        )

        return resp

if __name__ == '__main__':

    recommender = Recommender()
    
    # test_user = 3458960
    # recommend_item = recommender.get_top_n_items_recommend(user_id = test_user, n = 10)
    # print(recommend_item)
    # rfm_type = recommender.get_rfm_category(3458960)
    # resp = recommender.get_user_resp(3458960)

    # print(resp.user_info)
    # print(resp.rfm)
    # print(resp.item)
    # print(resp.friend)
    # print(resp.partner)

    # recom_item = recommender.get_top_n_items_recommend(26258912, 10)
    # recom_user = recommender.get_top_n_users_recommend(52216, 10)

    # rint('Item recommend')
    # print(recom_item)
    # print('User recommend')
    # print(recom_user)
    # rint(top_5_user)
    
    ''' Test item basket analysis function
    '''
    item_id = 52195
    # print(recommender.get_top_customer(item_id))
    # _pair, _set = recommender.get_item_basket(item_id)
    # print('Top 5 pair')
    # print(_pair)
    # print('Top 5 set')
    # print(_set)

    item_resp = recommender.get_item_resp(item_id)
    print(item_resp.server_stat)
    # print(item_resp.item_cate)
    # print(item_resp.baskset_pair)
    # print(item_resp.baskset_set)
    # print(item_resp.basic_info)