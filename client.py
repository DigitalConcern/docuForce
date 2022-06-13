import requests
import datetime


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
            ctr = 0
            for org in orgs:
                result[f"{ctr}"] = (org["name"], org["oguid"])
                ctr += 1
            return result


async def get_tasks_dict(p_access, p_refresh, org_code) -> dict:
    headers = {"Access-Token": f"{p_access}"}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_code)}/flows/tasks"
    # print(response.status_code, response.json(), sep='\n')
    params = {'showMode': "NEED_TO_ACTION",
              'isCompleted': "false"}
    while True:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            await get_access(p_refresh)
        else:
            tasks = response.json()
            result = {}
            ctr = 0
            for task in tasks:
                try:
                    cost = "Сумма: " + str(task["document"]["fields"]["sumTotal"]) + " " + str(
                        task["document"]["fields"]["currency"]) + "\n "
                except:
                    cost = ""
                try:
                    org__name = task["document"]["contractor"] + "\n"
                except:
                    org__name = ""
                try:
                    data = " От " + datetime.datetime.fromtimestamp(
                        task["document"]["documentTimestamp"] / 1e3).strftime("%d.%m.%Y") + "\n"
                except:
                    data = ""
                try:
                    doc_index = "№" + str(task["document"]["indexKey"])
                    if data == "":
                        doc_index += "\n"
                except:
                    doc_index = ""

                result[f"{ctr}"] = (cost,
                                    org__name,
                                    data,
                                    task["document"]["oguid"],
                                    doc_index,
                                    )  # Найти какие данные нужно вытащить из тасков
                ctr += 1
            return result


async def get_doc_dict(p_access, p_refresh, org_code, doc_code, page) -> str:
    headers = {"Access-Token": f"{p_access}"}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_code}/documents/{doc_code}/page/{page}"
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            await get_access(p_refresh)
        else:
            len = response.headers.get("X-Total-Pages")
            binar = response.text
            return {"len": len,
                    "image_bin": binar}
