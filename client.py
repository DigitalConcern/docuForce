from typing import Dict

import requests
import datetime

from bot import MyBot


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
                    org__name = task["document"]["fields"]["contractor"] + "\n"
                except:
                    org__name = ""
                try:
                    data = " От " + datetime.datetime.fromtimestamp(
                        task["document"]["fields"]["documentDate"] / 1e3).strftime("%d.%m.%Y") + "\n"
                except:
                    data = ""
                try:
                    doc_index = "№" + str(task["document"]["fields"]["documentNumber"])
                    if data == "":
                        doc_index += "\n"
                except:
                    doc_index = ""
                try:
                    doc_key = str(task["document"]["type"])
                    metaurl = f'https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_code)}/documentTypes/{doc_key}'
                    meta_response = requests.get(metaurl, headers=headers)
                    doc_name = meta_response.json()["titles"]["ru"]
                except:
                    doc_name = ""
                result[f"{ctr}"] = (cost,
                                    org__name,
                                    data,
                                    task["document"]["oguid"],
                                    doc_index, doc_name
                                    )  # Найти какие данные нужно вытащить из тасков
                ctr += 1
            return result


async def get_doc_dict(p_access, p_refresh, org_code, doc_code, page):
    headers = {"Access-Token": f"{p_access}"}
    page_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_code}/documents/{doc_code}/page/{page}"
    page_response = requests.get(page_url, headers=headers)
    while page_response.status_code != 200:
        await get_access(p_refresh)
    len = page_response.headers.get("X-Total-Pages")
    binary_img = page_response.text

    doc_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_code}/documents/{doc_code}"
    doc_response = requests.get(doc_url, headers=headers)
    while doc_response.status_code != 200:
        await get_access(p_refresh)
    doc_response_json = doc_response.json()
    try:
        doc_task_id = doc_response_json["tasks"][0]["oguid"]
        doc_task_type = doc_response_json["tasks"][0]["type"]
        doc_task_type_service = doc_response_json["tasks"][0]["taskType"]
    except:
        doc_task_id = ""
        doc_task_type = ""
        doc_task_type_service=""

    task_type_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_code}/routes/flowStageTypes"
    headers = {"Access-Token": f"{p_access}", "Accept-Language": "ru"}
    type_response = requests.get(task_type_url, headers=headers)
    while type_response.status_code != 200:
        await get_access(p_refresh)
    types_response_json = type_response.json()
    doc_task_name = ""
    for type in types_response_json:
        if type["type"] == doc_task_type:
            doc_task_name = type["buttonCaption"]

    return {"len": len,
            "image_bin": binary_img,
            "task_id": doc_task_id,
            "task_type": doc_task_name,
            "task_type_service": doc_task_type_service}


async def post_doc_action(p_access, p_refresh, org_id, task_id, action, user_id):
    headers = {"Access-Token": f"{p_access}",'content-type': 'application/json'}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/flows/tasks/{task_id}/complete"
    # print(response.status_code, response.json(), sep='\n')
    action_response = requests.post(url, headers=headers, json={"result": action})

    while (action_response.status_code == 400) or (action_response.status_code == 500):
        await get_access(p_refresh)
        action_response = requests.post(url, headers=headers, json={"result": action})

    if action_response.status_code == 409:
        for error in action_response.json():
            MyBot.bot.send_message(user_id, error["errorMessage"])
    print(action_response)
