from fastapi import FastAPI, Path, Depends
from fastapi.responses import JSONResponse
from app.data.items import item_data
from app.data.store import store_data
from app.models.api import LoginData


store_name_list = [store['Store_Name'] for store in store_data["Bangalore Outlet Details"]]
item_name_list = []
for item in item_data["Data"]:
    if item['outOfStock']!="FALSE":
        item_name_list.append(item['name'])
store_item_map = {}

for store in store_name_list:
    store_item_map[store] = {}
    for item_info in item_data['Data']:
        if item_info['outOfStock']!="FALSE":
            store_item_map[store][item_info['name']] = item_info
    print(len(store_item_map[store].keys()), "COUNT")


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

@app.post(f"/login")
def loginUser(loginData: LoginData):
    if loginData.uname not in userLoginDetails:
        return JSONResponse(status_code=400, content={'success': False})
    else:
        if (hash(loginData.password)==userLoginDetails[loginData.uname]):
            return JSONResponse(status_code=200, content={'success': True})
        else:
            return JSONResponse(status_code=400, content={'success': False})


@app.get("/get_store_details/{store_name}")
def get_store_details(store_name: str):
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

@app.get("/get_item_details/{item_name}")
def get_item_details(item_name: str):
    if(item_name not in item_name_list):
        return JSONResponse(status_code=200, content = {'success': True,
        'data': item_data["Data"]})
    else:
         return JSONResponse(status_code=200, content = {'success': True,
        'data': [item_data["Data"][item_name_list.index(item_name)]]})
