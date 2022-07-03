from fastapi import FastAPI, Path, Depends
from fastapi.responses import JSONResponse
from app.data.items import item_data
from app.data.store import store_data
from app.models.api import LoginData, NearestStore
import geopy.distance
import jwt
import time
from app.core.config import settings
from app.helpers.preprocessing import *
from fastapi.middleware.cors import CORSMiddleware
from copy import deepcopy
import requests


userLoginDetails = {
    'Santosh': {'pass': hash('passoword'), 'current_token': 1, 'mobile': '8277607950', 'email':
    'santoanand2@gmail.com'}
}

orderHistory = {}
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store_name_list = [store['Store_Name'] for store in store_data["Bangalore Outlet Details"]]
item_name_list = get_item_list()
item_data = preprocess_item_dict(deepcopy(item_data))
store_item_map = get_store_item_map(store_name_list, item_data)

@app.get("/validate_token/{token}")
def validate_token(token: str):
    try:
        decode_data = jwt.decode(token, settings.SECRET, algorithms=["HS256"])
        print("decoded data", decode_data)
        if (int(decode_data['expiry'])<=int(time.time()) or decode_data['token_count']>userLoginDetails[decode_data['username']]['current_token']):
            return JSONResponse(status_code=401, content={'success': False})
        return JSONResponse(status_code=200, content={'success': True})
    except jwt.exceptions.InvalidSignatureError as e:
        return JSONResponse(status_code=401, content={'success': False})


@app.post(f"/login")
def loginUser(loginData: LoginData):
    if loginData.uname not in userLoginDetails:
        return JSONResponse(status_code=400, content={'success': False})
    else:
        if (hash(loginData.password)==userLoginDetails[loginData.uname]['pass']):
            jwt_payload = {
                    "expiry": int(time.time()+600),
                    "username": loginData.uname,
                    "token_count": userLoginDetails[loginData.uname]['current_token']
                }
            encoded_jwt = jwt.encode(jwt_payload, settings.SECRET, algorithm="HS256")
            return JSONResponse(status_code=200, content={'success': True, 'token': encoded_jwt})
        else:
            return JSONResponse(status_code=400, content={'success': False})

@app.get("/get_store_details/{store_name}/{token}")
def get_store_details(store_name: str, token: str):
    result = validate_token(token=token)
    if result.status_code!=200:
       return JSONResponse(status_code=401, content={'success': False})
    if(store_name not in store_name_list):
        return_val = []
        for store in store_name_list:
            return_val.append({**store_data["Bangalore Outlet Details"][store_name_list.index(store)]
            , 'item_count': getTotalItemWithinAStore(store, store_item_map)})
        return JSONResponse(status_code=200, content = {'success': True,
        'data': return_val})
    else:
        total_item_count = getTotalItemWithinAStore(store_name, store_item_map)
        return JSONResponse(status_code=200, content = {'success': True,
        'data': {**store_data["Bangalore Outlet Details"][store_name_list.index(store_name)]
        , 'item_count': total_item_count}
        })
@app.get("/get_store_item_details/{store_name}/{item_name}/{token}")
def get_store_item_detail(store_name: str, item_name: str, token: str):
    result = validate_token(token=token)
    if result.status_code!=200:
       return JSONResponse(status_code=401, content={'success': False})

    return JSONResponse(status_code=200, content = {'success': True,
        'data': store_item_map[store_name][item_name]})

@app.get("/logout/{token}")
def logout(token: str):
    result = validate_token(token=token)
    if result.status_code!=200:
       return JSONResponse(status_code=401, content={'success': False})
    else:
        decode_data = jwt.decode(token, settings.SECRET, algorithms=["HS256"])
        userLoginDetails[decode_data['username']]['current_token']+=1

@app.get("/get_item_details/{token}")
def get_item_details(token: str):
    result = validate_token(token=token)
    if result.status_code!=200:
       return JSONResponse(status_code=401, content={'success': False})
    return JSONResponse(status_code=200, content = {'success': True,
        'data': item_data["Data"]})
    
@app.post("/get_nearest_store_and_get_payment_token/{token}")
def get_nearest_store_and_get_payment_token(token:str, input: NearestStore):
    result = validate_token(token=token)
    total_order_amount = 0
    if result.status_code!=200:
       return JSONResponse(status_code=401, content={'success': False})

    viable_candidates = []
    order_id = int(time.time())
    decode_data = jwt.decode(token, settings.SECRET, algorithms=["HS256"])
    for store in store_item_map:
        flag = False
        for item,count in input.item_details:
            if(int(store_item_map[store][item]['availableQuantity'])<count):
                flag = True
                break
        if flag is False:
            viable_candidates.append(store)

    min_distance = 1e10
    for store in viable_candidates:
        lat = store_data["Bangalore Outlet Details"][store_name_list.index(store)]["Latitude"]
        lon = store_data["Bangalore Outlet Details"][store_name_list.index(store)]["Longitude"]

        if(geopy.distance.geodesic((lat, lon), (input.user_location.lat, 
        input.user_location.lon)).km<min_distance):
            min_distance = geopy.distance.geodesic((lat, lon), (input.user_location.lat, 
        input.user_location.lon)).km
            best_store = store
            store_coord = [float(lat), float(lon)]

    for item,count in input.item_details:
        total_order_amount+=(int(store_item_map[best_store][item]['mrp'])*
                (1-int(store_item_map[best_store][item]['discountPercent'])/100)*count)
    payload = {"customer_details": {
        "customer_id":  decode_data['username'],
        "customer_email":  userLoginDetails[decode_data['username']]['email'],
        "customer_phone": userLoginDetails[decode_data['username']]['mobile']
    },  "order_id": str(order_id),"order_amount": total_order_amount,"order_currency": "INR"}

    headers = {
    "Accept": "application/json",
    "x-client-id": settings.CASHFREE_APPID,
    "x-client-secret": settings.CASHFREE_SECRETKEY,
    "x-api-version": "2022-01-01",
    "Content-Type": "application/json"}

    orderHistory[decode_data['username']] = orderHistory.get(decode_data['username'], [])
    orderHistory[decode_data['username']].append({'order_id': order_id, 'order_summary': input})

    response = requests.post(settings.CASHFREE_ENDPOINT+"/orders", json=payload, headers=headers)

    return JSONResponse(status_code=200, content = {'success': True,
        'data': {'store_name': best_store, 'store_coordinates': store_coord},
        'distance': min_distance, 'order_token': response["order_token"]})
        