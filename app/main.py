from fastapi import FastAPI, Path, Depends
from fastapi.responses import JSONResponse
from app.data.items import item_data
from app.data.store import store_data
from app.models.api import LoginData, NearestStore
import geopy.distance
import jwt
import time
from app.core.config import settings


store_name_list = [store['Store_Name'] for store in store_data["Bangalore Outlet Details"]]
item_name_list = []
for item in item_data["Data"]:
    if item['outOfStock']=="FALSE":
        item_name_list.append(item['name'])
store_item_map = {}

for store in store_name_list:
    store_item_map[store] = {}
    for item_info in item_data['Data']:
        if item_info['outOfStock']=="FALSE":
            store_item_map[store][item_info['name']] = item_info


def getTotalItemWithinAStore(store: str):
    item_count = 0
    for item in store_item_map[store].values():
        if (int(item['quantity'])>0):
            item_count+=1
    return item_count

app = FastAPI()

userLoginDetails = {
    'Santosh': hash('passoword')
}

@app.get("/validate_token/{token}")
def validate_token(token: str):
    try:
        decode_data = jwt.decode(token, settings.SECRET, algorithms=["HS256"])
        print("decoded data", decode_data, type(decode_data['token_id']))
        if (int(decode_data['expiry'])>=time.time()):
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
            , 'item_count': getTotalItemWithinAStore(store)})
        return JSONResponse(status_code=200, content = {'success': True,
        'data': return_val})
    else:
        total_item_count = getTotalItemWithinAStore(store_name)
        return JSONResponse(status_code=200, content = {'success': True,
        'data': {**store_data["Bangalore Outlet Details"][store_name_list.index(store_name)]
        , 'item_count': total_item_count}
        })

@app.get("/get_item_details/{item_name}/{token}")
def get_item_details(item_name: str, token: str):
    result = validate_token(token=token)
    if result.status_code!=200:
       return JSONResponse(status_code=401, content={'success': False})
    if(item_name not in item_name_list):
        return JSONResponse(status_code=200, content = {'success': True,
        'data': item_data["Data"]})
    else:
         return JSONResponse(status_code=200, content = {'success': True,
        'data': [item_data["Data"][item_name_list.index(item_name)]]})


@app.post("/get_nearest_store/{token}")
def get_nearest_store(token:str, input: NearestStore):
    result = validate_token(token=token)
    if result.status_code!=200:
       return JSONResponse(status_code=401, content={'success': False})
    viable_candidates = []
    for store in store_item_map:
        flag = False
        for item_count in input.item_details:
            item = item_count.item
            count = item_count.count
            if(int(store_item_map[store][item]['quantity'])<count):
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
        