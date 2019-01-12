import sys
sys.path.append('/Users/hsnu130427/BigdataCourse/Recommender/')
import logging
from datetime import datetime, timedelta

from sklearn.decomposition import PCA
import random
import pandas as pd
import numpy as np

from db_setting import data_resource

class UserRecommender():

    # def __init__(self):
    

    def get_login_recommend(self, user_id):
        ''' look into the past 1 month data
        '''

        login = data_resource.Login()
        login_record = login.get_data()
        logging.info('Get login record data')
        # now = datetime.now() # we don't have all data
        now = max(set(login_record.LoginDate))
        a_month_ago = now - timedelta(days=30)

        # query database to get a month data
        tar_df = login_record.loc[(login_record.LoginDate > a_month_ago) & (login_record.LoginDate < now)]
        tar_pivot = tar_df.pivot_table(index='UID', columns='LoginDate', values='LoginTime').fillna(0).astype('int64')
        
        # compare vector distance
        target = tar_pivot.loc[tar_pivot.index == user_id]
        other = tar_pivot.loc[tar_pivot.index != user_id]

        dist = other.apply(lambda x: np.linalg.norm(target.values - x.values), axis=1)
        outcome = pd.DataFrame({'id': other.index, 'dist': dist})
        similar_login_list = outcome.loc[outcome.dist==max(outcome.dist)].id.tolist()
        similar_login_list = [int(uid.split(' ')[0]) for uid in similar_login_list]
        print('{} people has same login record with this user.'.format(len(similar_login_list)))
        return similar_login_list

    def get_social_feature_recommend(self, user_id, n):
        
        # get total character data
        character = data_resource.character       
        tar_col = ['CashAmount', 'P1','P2','P3','P4','P5','P6','P7','P8', '1stRein', '2ndRein','ReinTimes']
        chara_clu_df = character[tar_col]
        
        # use pca to reduce dimension
        # pca = PCA(n_components=5)  
        # pca.fit(chara_clu_df.values)
        # X = pca.fit_transform(chara_clu_df.values)
        # pca_chara = pd.DataFrame(X, index=character.UID.values).iloc[:,:2]

        ####
        pca_chara = pd.read_csv('precomputed_data/pca_2d.csv')
        pca_chara.index = [int(x) for x in pca_chara.index]
        ####

        # pca and original data from given user
        tar_df = pca_chara.loc[pca_chara.index == user_id]
        ran_num = random.sample(range(tar_df.shape[0]), 1)[0]
        tar_data = tar_df.iloc[ran_num,:]
        tar_original = character.loc[character.UID == user_id]
        tar_original = tar_original.iloc[ran_num,:]

        # compute dist with each entry
        print('--------------- Start to compute Distance -----------------')
        '''
        init_dist = []
        init_index = []
        for index, entry in pca_chara.iloc[:,:].iterrows():
            dist = np.linalg.norm(tar_data.values - entry.values)
            init_dist.append(dist)
            init_index.append(index)
        print('--------------- Finishing Computation --------------')
        
        dist_df = pd.DataFrame({'UID': init_index,'Dist': init_dist})
        '''
        ###
        path = 'precomputed_data/test_dist_' + str(user_id) + '.csv' 
        # dist_df.to_csv(path)
        # print('Vector Distance for id {} is saved'.format(str(user_id)))
        dist_df = pd.read_csv(path)
        print(dist_df.shape)
        ####
        
        dist_df = dist_df.loc[dist_df.UID!=user_id,:]
        top_n_df = dist_df.sort_values('Dist').iloc[:n,:]
        top_n_recom_friend = top_n_df.UID.tolist()
        print(top_n_recom_friend)

        top_n_recom_friend_df = character.loc[(character.UID.apply(lambda x: x in top_n_recom_friend)) & (character.ServerNo == tar_original.ServerNo)]
        print(top_n_recom_friend_df)
        partner = []
        for uid in top_n_recom_friend_df.UID.tolist():
            if uid in character.UID.tolist():
                represent_recom = (character.loc[character.UID == uid]).sample(n=1) # each user can have several character
                recom_gender = represent_recom.Gender.values[0]
                if recom_gender != tar_original.Gender:
                    # partner.append((represent_recom.CharaID, represent_recom.UID))
                    # partner.append(uid)
                    partner.append(represent_recom)
        print(partner)
        
        partner_df = pd.concat(partner)

        return tar_original ,top_n_recom_friend_df, partner_df
        
    def get_friend_partner_recommend(self, user_id):

        # login_recommend = self.get_login_recommend(user_id)
        user_data, top_n_friend, partner = self.get_social_feature_recommend(user_id, 200)

        # # top_5_friend = list(set(login_recommend) & set(top_n_friend))[:5]
        # common_user = []
        # print('----- check friend -----')
        # for login_user in top_n_friend.UID.tolist():
        #     if login_user in login_recommend:
        #         print(login_user)
        #         common_user.append(login_user)

        # # partner = list(set(login_recommend) & set(partner))
        # partner_common = []
        # print('----- check partner ----')
        # for login_user in partner.UID.tolist():
        #     if login_user in login_recommend:
        #         print(login_user)
        #         partner_common.append(login_user)
        
        partner = partner.sample(n=1)

        if partner.UID.values in top_n_friend.UID.tolist():
            top_n_friend = top_n_friend.loc[partner.UID.values != top_n_friend.UID.tolist()]
        
        top_5_friend = ((top_n_friend.sample(n=5))[['CharaID', 'Career', 'Gender']]).values.tolist()
        print(user_data)
        print(top_5_friend)
        user_information = [user_data.UID, user_data.CharaID, user_data.CashAmount]
        partner = [partner.CharaID.values[0], partner.Career.values[0], partner.CashAmount.values[0]]
        return user_information, top_5_friend, partner


if __name__ == "__main__":

    
    user_recommend = UserRecommender()
    
    # candidate = user_recommend.get_login_recommend(1290944)
    # user_infomation, friend, partner = user_recommend.get_friend_partner_recommend(3458960)
    # print('User info: ')
    # print(user_infomation)
    # print('Recommend friends: ')
    # print(friend)
    # print('Recommend Partner: ')
    # print(partner)

    common_user = pd.read_table('precomputed_data/FourDatasetCommonUser.txt')
    common_user_list = common_user.values
    user_id_list = []

    for index, user in enumerate(common_user_list):
        user_id = int((user[0]).split(',')[1])
        user_id_list.append(user_id)

    user_id_list = random.sample(user_id_list, 100)
    count = 0
    for i in user_id_list:

        try:
            user_recommend.get_social_feature_recommend(i, 10)
            count += 1
        except:
            print('User id {} error occur'.format(i))
        
        if count > 10:
            break