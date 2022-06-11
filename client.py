import requests


async def sign_in(p_login, p_password) -> (str, str):
    headers = {'content-type': 'application/json'}
    data = {
        "email": p_login,
        "password": p_password
    }
    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/signin"

    response = requests.post(url, json=data, headers=headers)
    # print(response.status_code, response.json(), sep='\n')

    if response.status_code != 200:
        return False
    else:
        access = response.json()["access"]
        refresh = response.json()["refresh"]

        return access["value"], refresh["value"]


async def get_access(p_refresh) -> str:
    headers = {'content-type': 'application/json'}
    data = {
        "value": f"{p_refresh}",
    }
    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/token-refresh"

    response = requests.post(url, json=data, headers=headers)
    # print(response.status_code, response.json(), sep='\n')

    if response.status_code != 200:
        await get_access(p_refresh)
    else:
        access = response.json()["access"]
        return access["value"]


async def get_orgs_dict(p_access, p_refresh) -> dict:
    headers = {"Access-Token": f"{p_access}"}
    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/user"
    # print(response.status_code, response.json(), sep='\n')

    while True:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            await get_access(p_refresh)
        else:
            orgs = response.json()["orgs"]
            result = {}
            ctr = 1
            for org in orgs:
                result[f"{ctr}"] = (org["name"], org["oguid"])
                ctr += 1
            return result

