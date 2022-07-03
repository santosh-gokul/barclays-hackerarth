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


userLoginDetails = {
    'Santosh': hash('passoword')
}

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
        if (int(decode_data['expiry'])<=int(time.time())):
            return JSONResponse(status_code=401, content={'success': False})
        return JSONResponse(status_code=200, content={'success': True})
    except jwt.exceptions.InvalidSignatureError as e:
        return JSONResponse(status_code=401, content={'success': False})


@app.post(f"/login")
def loginUser(loginData: LoginData):
    if loginData.uname not in userLoginDetails:
        return JSONResponse(status_code=400, content={'success': False})
    else:
        if (hash(loginData.password)==userLoginDetails[loginData.uname]):
            jwt_payload = {
                    "expiry": int(time.time()+600),
                    "username": loginData.uname,
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

@app.get("/get_item_details/{token}")
def get_item_details(token: str):
    result = validate_token(token=token)
    if result.status_code!=200:
       return JSONResponse(status_code=401, content={'success': False})
    return JSONResponse(status_code=200, content = {'success': True,
        'data': item_data["Data"]})
    
@app.post("/get_nearest_store/{token}")
def get_nearest_store(token:str, input: NearestStore):
    result = validate_token(token=token)
    if result.status_code!=200:
       return JSONResponse(status_code=401, content={'success': False})
    viable_candidates = []
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
    
    return JSONResponse(status_code=200, content = {'success': True,
        'data': {'store_name': best_store, 'store_coordinates': store_coord},
        'distance': min_distance})
        