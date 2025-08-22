import os
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth

from dotenv import load_dotenv

load_dotenv()

username=os.getenv('username')
password=os.getenv('password')




host='https://api.worldquantbrain.com'

def login(session):
    session.auth = HTTPBasicAuth(username, password)
    response = session.post(f"{host}/authentication")
    print(response.status_code)
    print(response.json())

offset = 100
limit = 100

# lines = []
# with open("fields.txt", "r") as f:
#     for i, line in enumerate(f):
#         if i < offset:
#             continue
#         if i >= offset + limit:
#             break
#         lines.append(line.strip())
lines = [
         'cash_st', 'cashflow', 'cashflow_dividends'
        #  , 'cashflow_fin', 'cashflow_invst', 'cashflow_op', 'cogs', 'current_ratio', 'debt', 'debt_lt', 'debt_st', 'depre_amort', 'ebit', 'ebitda', 'employee', 'enterprise_value', 'eps', 'equity', 'fnd6_acdo', 'fnd6_acodo', 'fnd6_acox', 'fnd6_acqgdwl', 'fnd6_acqintan', 'fnd6_adesinda_curcd', 'fnd6_aldo', 'fnd6_am', 'fnd6_aodo', 'fnd6_aox', 'fnd6_aqc', 'fnd6_aqi', 'fnd6_aqs', 'fnd6_beta', 'fnd6_capxv', 'fnd6_ceql', 'fnd6_ch', 'fnd6_ci', 'fnd6_cibegni', 'fnd6_cicurr', 'fnd6_cidergl', 'fnd6_cik', 'fnd6_cimii', 'fnd6_ciother', 'fnd6_cipen', 'fnd6_cisecgl', 'fnd6_citotal', 'fnd6_city', 'fnd6_cld2', 'fnd6_cld3', 'fnd6_cld4', 'fnd6_cld5', 'fnd6_cptmfmq_actq', 'fnd6_cptmfmq_atq', 'fnd6_cptmfmq_ceqq', 'fnd6_cptmfmq_dlttq', 'fnd6_cptmfmq_dpq', 'fnd6_cptmfmq_lctq', 'fnd6_cptmfmq_oibdpq', 'fnd6_cptmfmq_opepsq', 'fnd6_cptmfmq_saleq', 'fnd6_cptnewqv1300_actq', 'fnd6_cptnewqv1300_apq', 'fnd6_cptnewqv1300_atq', 'fnd6_cptnewqv1300_ceqq', 'fnd6_cptnewqv1300_dlttq', 'fnd6_cptnewqv1300_dpq', 'fnd6_cptnewqv1300_epsf12', 'fnd6_cptnewqv1300_epsfxq', 'fnd6_cptnewqv1300_epsx12', 'fnd6_cptnewqv1300_lctq', 'fnd6_cptnewqv1300_ltq', 'fnd6_cptnewqv1300_nopiq', 'fnd6_cptnewqv1300_oeps12', 'fnd6_cptnewqv1300_oiadpq', 'fnd6_cptnewqv1300_oibdpq', 'fnd6_cptnewqv1300_opepsq', 'fnd6_cptnewqv1300_rectq', 'fnd6_cptnewqv1300_req', 'fnd6_cptnewqv1300_saleq', 'fnd6_cptrank_gvkeymap', 'fnd6_cshpri', 'fnd6_cshr', 'fnd6_cshtr', 'fnd6_cshtrq', 'fnd6_cstkcv', 'fnd6_cstkcvq', 'fnd6_currencya_curcd', 'fnd6_currencyqv1300_curcd', 'fnd6_dc', 'fnd6_dclo', 'fnd6_dcpstk', 'fnd6_dcvsr', 'fnd6_dcvsub', 'fnd6_dcvt', 'fnd6_dd'
         ]

def build_alpha(field):
    alpha_exp = f"group_rank({field}/cap, subindustry)"
    simulation_data = {
        'type':'REGULAR',
        'settings':{
            'instrumentType':'EQUITY',
            'region':'USA',
            'universe':'TOP3000',
            'delay':1,
            'decay':0,
            'neutralization':'SUBINDUSTRY',
            'truncation':0.08,
            'pasteurization':'ON',
            'unitHandling':'VERIFY',
            'nanHandling':'ON',
            'language':'FASTEXPR',
            'visualization':False
        },
        'regular': alpha_exp
    }
    return simulation_data

alphas = [build_alpha(line) for line in lines]

def run_alpha(alpha):
    from time import sleep
    
    # login
    session = requests.Session()
    login(session)
    
    print(f"run alpha: {alpha}")    
    sim_resp = session.post(
        f'{host}/simulations',
        json = alpha,
    )
    try:
        sim_progress_url = sim_resp.headers['Location']
        while True:
            sim_progress_resp = session.get(sim_progress_url)
            retry_after_sec = float(sim_progress_resp.headers.get("retry-After",0))
            if retry_after_sec == 0 :
                break
            sleep(retry_after_sec)

        response = sim_progress_resp.json()
        alpha_id = response["alpha"]
        print(f"Alpha ID: {alpha_id}")
    except:
        print('no location, try again')
        sleep(10)

for i, alpha in enumerate(alphas):
    run_alpha(alpha)
