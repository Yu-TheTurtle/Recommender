from flask import Flask, request, render_template,redirect
from recommender import Recommender

import WTForm

app = Flask(__name__)

recommender_agent = Recommender()

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/user_query', methods=['GET', 'POST'])
def user_query():
    # form = WTForm.UserForm()
    return render_template('user_query.html')

@app.route('/user_result', methods=['GET', 'POST'])
def user_result():

    user_id = int(request.args.get('user_id'))
    print('Start to get recommendation based on user_id: {}'.format(user_id))
    resp = recommender_agent.get_user_resp(user_id)

    print(resp.user_info)
    print(resp.friend)
    print(resp.item)
    print(resp.partner)
    print(resp.rfm)

    return render_template('user_result.html', 
                user_id = user_id,
                basic_information = resp.user_info,
                rfm_type = resp.rfm,
                items = resp.item, 
                friends = resp.friend, 
                recom_partner = resp.partner)

@app.route('/item_query', methods=['GET', 'POST'])
def item_query():
    # form = WTForm.ItemForm()
    return render_template('item_query.html')

@app.route('/item_result')
def item_result():

    item_id = int(request.args.get('item_id'))
    resp = recommender_agent.get_item_resp(item_id)
    print(resp.baskset_set)
    return render_template('item_result.html', 
                item_id = item_id,
                basic_info = resp.basic_info,
                server_stat = resp.server_stat,
                basket_pair = resp.baskset_pair,
                basket_set = resp.baskset_set, # [[a,b,c,d,e], support, confidence]
                top_customer = resp.top_customer)

if __name__ == '__main__':
    app.run(debug=True)