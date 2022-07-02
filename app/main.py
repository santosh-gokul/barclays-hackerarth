from fastapi import FastAPI, Path, Depends
from fastapi.responses import JSONResponse
from app.data.items import item_data
from app.data.store import store_data

app = FastAPI()

userLoginDetails = {
    'Santosh': hash('passoword')
}

@app.post(f"/login")
def loginUser(loginData: dict):
    if loginData['uname'] not in userLoginDetails:
        return JSONResponse(status_code=400, content={'success': False})
    else:
        if (hash(loginData['pass'])==userLoginDetails[loginData['uname']]):
            return JSONResponse(status_code=200, content={'success': True})
        else:
            return JSONResponse(status_code=400, content={'success': False})


@app.get("/get_store_details")
def get_store_details():
    return JSONResponse(status_code=200, content = {'success': True,
    'data': store_data["Bangalore Outlet Details"]})

@app.get("/get_item_details")
def get_item_details():
    return JSONResponse(status_code=200, content = {'success': True,
    'data': item_data["Data"]})