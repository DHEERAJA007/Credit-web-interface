from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import pickle
import numpy as np
import json
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    with open('model_pipeline.pkl', 'rb') as f:
        app.state.model = pickle.load(f)

    app.state.weights = pd.read_csv('scorecard.csv', index_col=0)

    with open('model_columns.json', 'r') as f:
        app.state.MODEL_INPUT_COLUMNS = json.load(f)

    with open("woe.pkl", "rb") as f:
        app.state.woe_map = pickle.load(f)

    yield

app = FastAPI(title='Restaurant Rating Predictor with AI Dashboard', lifespan=lifespan)

templates = Jinja2Templates(directory='templates')
app.mount('/static', StaticFiles(directory='static'), name='static')

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("app_uidashboard.html", {"request": request})

def bin_feature(feature, value):
    if feature == 'term':
        return 'term_bin:36.0' if '36' in str(value).strip() else 'term_bin:60.0'

    if feature in ['pub_rec', 'acc_now_delinq', 'delinq_2yrs', 'inq_last_6mths']:
        return f"{feature}_bin:{str(float(value))}"

    try:
        val = float(value)
    except ValueError:
        return value

    if feature == 'annual_inc':
        if val < 20000: return 'annual_inc_bin:<20000 thousands'
        elif val < 30000: return 'annual_inc_bin:20000-30000 thousands'
        elif val < 40000: return 'annual_inc_bin:30000-40000 thousands'
        elif val < 50000: return 'annual_inc_bin:40000-50000 thousands'
        elif val < 60000: return 'annual_inc_bin:50000-60000 thousands'
        elif val < 70000: return 'annual_inc_bin:60000-70000 thousands'
        elif val < 80000: return 'annual_inc_bin:70000-80000 thousands'
        elif val < 90000: return 'annual_inc_bin:80000-90000 thousands'
        elif val < 100000: return 'annual_inc_bin:90000-100000 thousands'
        elif val < 120000: return 'annual_inc_bin:100000-120000 thousands'
        elif val < 140000: return 'annual_inc_bin:120000-140000 thousands'
        else: return 'annual_inc_bin:>140000 thousands'
    elif feature == 'int_rate':
        if val < 9.61: return 'int_rate_bin:<9.61%'
        elif val < 12.025: return 'int_rate_bin:9.610% - 12.025%'
        elif val < 15.74: return 'int_rate_bin:12.025% - 15.74%'
        elif val < 20.281: return 'int_rate_bin:15.74% - 20.281%'
        else: return 'int_rate_bin:>20.281%'
    elif feature == 'dti':
        if val < 14: return 'dti_bin:<14%'
        elif val < 35: return 'dti_bin:14%-35%'
        elif val < 77: return 'dti_bin:35%-77%'
        elif val < 105: return 'dti_bin:77%-105%'
        elif val < 160: return 'dti_bin:105%-160%'
        elif val < 203: return 'dti_bin:161%-203%'
        elif val < 217: return 'dti_bin:203%-217%'
        elif val < 224: return 'dti_bin:217%-224%'
        elif val < 350: return 'dti_bin:224%-350%'
        else: return 'dti_bin:>350%'
    elif feature == 'months_since_credit_line':
        if val < 160: return 'months_since_credit_line_bin:<160'
        elif val < 250: return 'months_since_credit_line_bin:160-250'
        elif val < 340: return 'months_since_credit_line_bin:250-340'
        elif val < 430: return 'months_since_credit_line_bin:340-430'
        elif val < 520: return 'months_since_credit_line_bin:430-520'
        elif val < 610: return 'months_since_credit_line_bin:520-610'
        else: return 'months_since_credit_line_bin:>610'
    elif feature == 'total_rev_hi_lim':
        if val < 5000: return 'total_rev_hi_lim_bin:<5000 thousands'
        elif val < 10000: return 'total_rev_hi_lim_bin:5000-10000 thousands'
        elif val < 20000: return 'total_rev_hi_lim_bin:10000-20000 thousands'
        elif val < 30000: return 'total_rev_hi_lim_bin:20000-30000 thousands'
        elif val < 40000: return 'total_rev_hi_lim_bin:30000-40000 thousands'
        elif val < 55000: return 'total_rev_hi_lim_bin:40000-55000 thousands'
        elif val < 95000: return 'total_rev_hi_lim_bin:55000-95000 thousands'
        else: return 'total_rev_hi_lim_bin:>95000 thousands'
    elif feature == 'total_acc':
        if val < 25: return 'total_acc_bin:<25 Accounts'
        elif val <= 50: return 'total_acc_bin:25-50 Accounts'
        else: return 'total_acc_bin:>50 Accounts'
    elif feature == 'open_acc':
        if val == 0: return 'open_acc_bin:0 Accounts'
        elif val <= 3: return 'open_acc_bin:1-3 Accounts'
        elif val <= 12: return 'open_acc_bin:4-12 Accounts'
        elif val <= 17: return 'open_acc_bin:13-17 Accounts'
        elif val <= 22: return 'open_acc_bin:18-22 Accounts'
        elif val <= 25: return 'open_acc_bin:23-25 Accounts'
        elif val <= 30: return 'open_acc_bin:26-30 Accounts'
        else: return 'open_acc_bin:>31 Accounts'
    return value

def get_woe_value(feature, binned_value, woe_map):
    # Extract actual feature name and value
    if ':' in binned_value:
        feature_name, value_key = binned_value.split(':', 1)
    else:
        feature_name = feature if feature not in ['pub_rec', 'acc_now_delinq', 'delinq_2yrs', 'inq_last_6mths'] else f"{feature}_bin"
        value_key = binned_value

    # Lookup in woe_map
    woe_feature_dict = woe_map.get(feature_name, {})
    woe_value = woe_feature_dict.get(value_key)

    if woe_value is None:
        # Fuzzy match if needed
        cleaned_key = str(value_key).strip().replace(" ", "").lower()
        for k in woe_feature_dict:
            if cleaned_key == str(k).strip().replace(" ", "").lower():
                woe_value = woe_feature_dict[k]
                break

    return woe_value if woe_value is not None else 0.0




@app.post('/predict/', response_class=HTMLResponse)
async def predict(
    request: Request,
    annual_inc: str = Form(...),
    int_rate: str = Form(...),
    term: str = Form(...),
    home_ownership: str = Form(...),
    addr_state: str = Form(...),
    total_rev_hi_lim: str = Form(...),
    months_since_credit_line: str = Form(...),
    total_acc: str = Form(...),
    inq_last_6mths: str = Form(...),
    emp_length: str = Form(...),
    open_acc: str = Form(...),
    verification_status: str = Form(...),
    purpose: str = Form(...),
    dti: str = Form(...),
    delinq_2yrs: str = Form(...),
    acc_now_delinq: str = Form(...),
    pub_rec: str = Form(...),
    initial_list_status: str = Form(...)
):
    form_data = locals().copy()
    del form_data['request']

    model = request.app.state.model
    weights = request.app.state.weights
    MODEL_INPUT_COLUMNS = request.app.state.MODEL_INPUT_COLUMNS
    woe_map = request.app.state.woe_map

    input_df = pd.DataFrame(columns=MODEL_INPUT_COLUMNS)
    row = {}
    debug_output = []

    emp_map = {
        '1': '1 year', '2': '2 years', '3': '3 years', '4': '4 years', '5': '5 years',
        '6': '6 years', '7': '7 years', '8': '8 years', '9': '9 years',
        '10': '10 or more years', '15': '10 or more years', 'Unknown': 'Unknown'
    }

    for feature, value in form_data.items():
        key = value.strip()

        if feature == 'emp_length':
            key = emp_map.get(key, key)

        if feature in ['annual_inc', 'int_rate', 'dti', 'months_since_credit_line',
                       'total_rev_hi_lim', 'total_acc', 'open_acc', 'inq_last_6mths',
                       'pub_rec', 'acc_now_delinq', 'delinq_2yrs', 'term']:
            key = bin_feature(feature, key)

        print(f"Binned '{feature}': raw='{value}' => binned='{key}'")
        woe_feature = f"{feature}_woe"
        feature_woe_dict = woe_map.get(feature, {})
        woe_value = feature_woe_dict.get(key)

        if woe_value is None:
            cleaned_key = str(key).strip().replace(" ", "").lower()
            for k in feature_woe_dict:
                if cleaned_key == str(k).strip().replace(" ", "").lower():
                    woe_value = feature_woe_dict[k]
                    break

        if woe_value is None:
            print(f"❌ WARNING: '{key}' not found in WoE map for feature '{feature}'")
            woe_value = 0.0

        debug_output.append(f"{feature}: '{key}' => {woe_value}")
        row[woe_feature] = woe_value

    for col in MODEL_INPUT_COLUMNS:
        if col not in row:
            row[col] = 0.0

    input_df.loc[0] = row

    print("--- WOE Mapping Debug Info ---")
    for line in debug_output:
        print(line)
    print("--- END ---")

    probability_default = model.predict_proba(input_df)[0][1]

    score_weights = weights['Score - Weights'].dropna()
    common_features = input_df.columns.intersection(score_weights.index)
    weighted_scores = input_df[common_features] * score_weights.loc[common_features].values
    intercept = score_weights.get('Intercept', 0)
    raw_score = weighted_scores.sum(axis=1).values[0] + intercept

    mapped_score = int(np.clip(np.round(900 - 600 * probability_default, 0), 300, 900))
    credit_status = "Creditworthy" if mapped_score >= 620 else "Not Creditworthy"

    return templates.TemplateResponse("result.html", {
        "request": request,
        "probability": round(probability_default * 100, 2),
        "credit_score": mapped_score,
        "credit_status": credit_status
    })
