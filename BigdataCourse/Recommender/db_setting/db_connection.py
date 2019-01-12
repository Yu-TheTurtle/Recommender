from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import pandas as pd
from sqlalchemy.sql import select
from contextlib import contextmanager

from db_setting import orm

db_connect = 'mssql+pymssql://sa:Nccustat38@localhost:1433/Final'
# ref: https://stackoverflow.com/questions/19451490/how-to-identify-port-number-of-sql-server
engine = create_engine(db_connect, echo=True)
# SessionType = scoped_session(sessionmaker(
#         bind=engine, expire_on_commit=False
# ))

# def GetSession():
#     return SessionType()

# @contextmanager
# def session_scope():
#     session = GetSession()
#     try:
#         yield session
#         session.commit()
#     except:
#         session.rollback()
#         raise
#     finally:
#         session.close()

# def get_login_data():
#     with session_scope() as session:
#         return session.query(orm.Login)

if __name__ == '__main__':

    # data = get_login_data()
    # for record in data:
    #     print('{} logined'.format(record.uid))
    
    conn = engine.connect()
    s = select([orm.ItemServer])
    result = conn.execute(s)
    login = pd.read_sql(s, conn)
    print(login.head())
    # for index, row in enumerate(result):
    #    if index < 500:
    #        print('{}th row for id {} and logined at {}'.format(index, row.column1, row.column2))
    #    else: 
    #        print('Test owari')
    #        break
