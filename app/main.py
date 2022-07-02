from tkinter.tix import Tree
from fastapi import FastAPI, Path, Depends
from fastapi.responses import JSONResponse
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

    