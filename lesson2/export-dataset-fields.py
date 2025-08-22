import os
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth

from dotenv import load_dotenv

load_dotenv()

username=os.getenv('username')
password=os.getenv('password')

host='https://api.worldquantbrain.com'

# login
session = requests.Session()

def login(session):
    session.auth = HTTPBasicAuth(username, password)
    response = session.post(f"{host}/authentication")
    print(response.status_code)
    print(response.json())
    
login(session)

def get_data_fields(session, search_scope, dataset_id = '', search =''):
    import pandas as pd
    instrumentType = search_scope['instrumentType']
    region = search_scope['region']
    delay = str(search_scope['delay'])
    universe = search_scope['universe']
    if len(search) == 0:
        url_template = f"{host}/data-fields?" +\
            f"&instrumentType={instrumentType}" +\
            f"&region={region}&delay={delay}&universe={universe}" +\
            f"&dataset.id={dataset_id}&limit=50" +\
            "&offset={x}"
        url = url_template.format(x=0)
        count = session.get(url).json()['count']
    else:
        url_template = f"{host}/data-fields?" +\
            f"&instrumentType={instrumentType}" +\
            f"&region={region}&delay={delay}&universe={universe}" +\
            f"&dataset.id={dataset_id}&limit=50" +\
            f"&search={search}" +\
            "&offset={x}"
        count = 100

    data_fields = []
    for x in range(0, count, 50):
        url = url_template.format(x=x)
        response = session.get(url)
        data = response.json()
        data_fields.append(data['results'])
    data_fields_flat = [item for sublist in data_fields for item in sublist]
    data_fields_df = pd.DataFrame(data_fields_flat)
    return data_fields_df

search_scope = {
    'instrumentType': 'EQUITY',
    'region': 'USA',
    'delay': 1,
    'universe': 'TOP3000'
}
fd6_fields = get_data_fields(session, search_scope, "fundamental6")
fd6_matrix = fd6_fields[fd6_fields['type'] == 'MATRIX']
headers = fd6_matrix.head()
values = fd6_matrix['id'].values.tolist()

with open("fields.txt", "w") as f:
    for item in values:
        f.write(f"{item}\n")
    