import pandas as pd
import os, json
import requests
import hashlib
import numpy as np


# Hypothesis.is stores the data by user, so we'll use 'users' info to get data.
data = {
    'user': "Ezloplop",
    'group_text': "BehSci",
    'group': "Jk8bYJdN",
    'api_key': "my_api_key"
}

users = requests.get(url=f"https://api.hypothes.is/api/groups/{data['group']}/members")


url_search = "https://api.hypothes.is/api/search"
url_ = "https://hypothes.is/groups/Jk8bYJdN/behsci"

data_per_user = []
for user in users.json():
    print(user)
    user_id = user['userid']
    user_batch = []
    for i in range(0, 5000, 200):
        res = requests.get(url=url_search,
                           params={'group':'Jk8bYJdN', 'user':f'{user_id}', 'limit': 200, 'offset':i},
                           headers={'Authorization': f"Bearer {data['api_key']}"})
        user_batch.append(res.json())
    data_per_user.append(user_batch)

total_anns = []
for batch in data_per_user:
    for elem in batch:
        total_anns += elem['rows']

# Store the dataframe into json file
total_anns_df = pd.DataFrame(total_anns)
total_anns_df.to_json('hypothesis_v1__12-03-22.jsonl', orient='records', lines=True)