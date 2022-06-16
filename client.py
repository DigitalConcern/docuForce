from typing import Dict
from collections import defaultdict

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


async def get_user_id(p_access) -> str:
    headers = {"Access-Token": f"{p_access}"}

    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/user"

    response = requests.get(url, headers=headers)
    user_id = response.json()["oguid"]

    while response.status_code != 200:
        response = requests.post(url, headers=headers)
        user_id = response.json()["oguid"]

    return user_id


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
    headers = {"Access-Token": f"{p_access}", "Accept-Language": "ru"}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_code)}/flows/tasks"

    params = {'showMode': "NEED_TO_ACTION",
              'isCompleted': "false"}

    response = requests.get(url, headers=headers, params=params)
    while response.status_code != 200:
        await get_access(p_refresh)
        response = requests.get(url, headers=headers, params=params)

    types_headers = {"Access-Token": f"{p_access}", 'content-type': 'application/json', "Accept-Language": "ru"}
    types_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_code)}/routes/flowStageTypes"
    response_types = requests.get(types_url, headers=types_headers, params=params)

    response_types_list = response_types.json()

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
                    try:
                        doc_name = meta_response.json()["titles"]["ru"]
                    except:
                        try:
                            doc_name = meta_response.json()["title"]
                        except:
                            doc_name = meta_response.json()["titles"]["en"]
                    other_fields = ""
                    try:
                        # meta_fields = meta_response.json()["fields"]
                        for field in meta_response.json()["fields"]:
                            if field["formProperties"]["form"]["visible"] and (
                                    field["key"] not in ["sumTotal", "currency", "contractor", "documentDate",
                                                         "documentNumber"]):
                                try:
                                    other_fields += field["component"]["label"] + ": " + str(
                                        task["document"]["fields"][field["key"]])
                                except:
                                    other_fields += field["component"]["labels"]["ru"] + ": " + str(
                                        task["document"]["fields"][field["key"]]) + "\n"
                                print(other_fields)
                    except:
                        pass
                except:
                    doc_name = ""

                stage = "\n\n" + f"<i>Завершено</i>"
                for stage_type in response_types_list:
                    try:
                        if stage_type["type"] == task["document"]['flowStageType']:
                            stage = "\n\n" + f"<i>{stage_type['name']}</i>"
                    except:
                        stage = ""
                result[f"{ctr}"] = (cost,
                                    org__name,
                                    data,
                                    task["document"]["oguid"],
                                    doc_index,
                                    doc_name,
                                    other_fields,
                                    stage
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
        # doc_task_type_service = doc_response_json["tasks"][0]["taskType"]
    except:
        doc_task_id = ""
        doc_task_type = ""
        # doc_task_type_service = ""
    try:
        doc_att_id = doc_response_json["documentAttachmentOguid"]
    except:
        doc_att_id = ""

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
            "task_type_service": doc_task_type,
            "doc_att_id": doc_att_id}


async def post_doc_action(p_access, p_refresh, org_id, task_id, action, user_tg_id):
    headers = {"Access-Token": f"{p_access}", 'content-type': 'application/json'}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/flows/tasks/{task_id}/complete"
    # print(response.status_code, response.json(), sep='\n')
    action_response = requests.post(url, headers=headers, json={"result": action})

    while (action_response.status_code == 400) or (action_response.status_code == 500):
        await get_access(p_refresh)
        action_response = requests.post(url, headers=headers, json={"result": action})

    if action_response.status_code == 409:
        for error in action_response.json():
            MyBot.bot.send_message(user_tg_id, error["errorMessage"])
    print(action_response)


async def get_certificate(p_access, p_refresh, org_code, user_id):
    headers = {"Access-Token": f"{p_access}"}
    certif_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_code}/users/{user_id}/certificate"
    certif_response = requests.get(certif_url, headers=headers)
    while certif_response.status_code != 200:
        await get_access(p_refresh)
        certif_response = requests.get(certif_url, headers=headers)
    try:
        certif_id = certif_response.json()["oguid"]
        certif_standard = certif_response.json()["standard"]
    except:
        certif_id = ""
        certif_standard = ""
    return certif_id, certif_standard


async def post_hash(p_access, p_refresh, org_code, standard, doc_id):
    headers = {"Access-Token": f"{p_access}", 'content-type': 'application/json'}
    hash_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_code}/attachments/hash"
    data = {"standard": standard,
            "attachmentOguid": doc_id}
    # "uploadedFileOguid": doc_id}
    hash_response = requests.post(hash_url, headers=headers, json=data)
    while hash_response.status_code != 200:
        await get_access(p_refresh)
        hash_response = requests.post(hash_url, headers=headers, json=data)
    try:
        hash = hash_response.json()["hash"]
    except:
        hash = ""
    return hash


async def post_doc_sign(p_access, p_refresh, org_id, user_id, att_doc_id, doc_id):
    certif = await get_certificate(p_access, p_refresh, org_id, user_id)
    certif_id, certif_stand = certif[0], certif[1]
    if certif_id == "":
        return "ERROR"

    hash = await post_hash(p_access, p_refresh, org_id, certif_stand, att_doc_id)
    if hash == "":
        return "ERROR"

    headers = {"Access-Token": f"{p_access}", 'content-type': 'application/json'}
    sign_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/users/{user_id}/docuForceCertificate/{certif_id}/sign"
    sign_data = {"hash": hash}
    action_response = requests.post(sign_url, headers=headers, json=sign_data)

    while action_response.status_code != 201:
        await get_access(p_refresh)
        action_response = requests.post(sign_url, headers=headers, json=sign_data)

    add_sign_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/documents/{doc_id}/attachments/signatures"
    add_sign_data = {"oguid": action_response.text[1:-1],
                     "comment": ""}
    add_sign_response = requests.post(add_sign_url, headers=headers, json=add_sign_data)

    print(add_sign_response)
    return "SUCCESS"


async def get_doc_list(p_access, p_refresh, org_id, contained_string=""):
    headers = {"Access-Token": f"{p_access}", 'content-type': 'application/json'}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/documents"

    if contained_string == "":
        params = {}
    else:
        params = {"query.like": contained_string}

    response = requests.get(url, headers=headers, params=params)
    while response.status_code != 200:
        await get_access(p_refresh)
        response = requests.get(url, headers=headers, params=params)

    types_headers = {"Access-Token": f"{p_access}", 'content-type': 'application/json', "Accept-Language": "ru"}
    types_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/routes/flowStageTypes"
    response_types = requests.get(types_url, headers=types_headers, params=params)
    while response.status_code != 200:
        await get_access(p_refresh)
        response_types = requests.get(types_url, headers=types_headers, params=params)

    result = []
    resp_list = response.json()
    response_types_list = response_types.json()
    for resp in resp_list:
        try:
            cost = "Сумма: " + str(resp["fields"]["sumTotal"]) + " " + str(
                resp["fields"]["currency"]) + "\n"
        except:
            cost = ""
        try:
            org__name = resp["fields"]["contractor"] + "\n"
        except:
            org__name = ""
        try:
            data = " От " + datetime.datetime.fromtimestamp(
                resp["fields"]["documentDate"] / 1e3).strftime("%d.%m.%Y") + "\n"
        except:
            data = ""
        try:
            doc_index = "№" + str(resp["fields"]["documentNumber"])
            if data == "":
                doc_index += "\n"
        except:
            doc_index = ""
        try:
            doc_key = str(resp["type"])
            metaurl = f'https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/documentTypes/{doc_key}'
            meta_response = requests.get(metaurl, headers=headers)
            try:
                doc_name = meta_response.json()["titles"]["ru"]
            except:
                try:
                    doc_name = meta_response.json()["title"]
                except:
                    doc_name = meta_response.json()["titles"]["en"]
            other_fields = ""
            try:
                for field in meta_response.json()["fields"]:
                    if field["formProperties"]["form"]["visible"] and (
                            field["key"] not in ["sumTotal", "currency", "contractor", "documentDate",
                                                 "documentNumber"]):
                        try:
                            other_fields += field["component"]["label"] + ": " + str(
                                resp["fields"][field["key"]])
                        except:
                            other_fields += field["component"]["labels"]["ru"] + ": " + str(
                                resp["fields"][field["key"]]) + "\n"
                        print(other_fields)
            except:
                pass
        except:
            pass

        try:
            doc_id = resp["oguid"]
        except:
            doc_id = ""

        stage = "\n\n" + f"<i>Завершено</i>"
        for stage_type in response_types_list:
            try:
                if stage_type["type"] == resp['flowStageType']:
                    stage = "\n\n" + f"<i>{stage_type['name']}</i>"
            except:
                stage = ""

        result.append((cost, org__name, data, doc_index, doc_name, doc_id, other_fields, stage))

    return result


async def get_messages_dict(p_access, p_refresh, org_code):
    headers = {"Access-Token": f"{p_access}", "Accept-Language": "ru"}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_code)}/flows/tasks"

    params = {'showMode': "TODOS_ONLY",
              'isCompleted': "false"}

    response = requests.get(url, headers=headers, params=params)
    while response.status_code != 200:
        await get_access(p_refresh)
        response = requests.get(url, headers=headers, params=params)

    types_headers = {"Access-Token": f"{p_access}", 'content-type': 'application/json', "Accept-Language": "ru"}
    types_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_code)}/routes/flowStageTypes"
    response_types = requests.get(types_url, headers=types_headers, params=params)

    response_types_list = response_types.json()
    conversations = response.json()

    result = {}
    messages = defaultdict(list)
    ctr = 0
    for conversation in conversations:
        try:
            cost = "Сумма: " + str(conversation["document"]["fields"]["sumTotal"]) + " " + str(
                conversation["document"]["fields"]["currency"])
        except:
            cost = ""
        try:
            org__name = conversation["document"]["fields"]["contractor"] + "\n"
        except:
            org__name = ""
        try:
            data = " От " + datetime.datetime.fromtimestamp(
                conversation["document"]["fields"]["documentDate"] / 1e3).strftime("%d.%m.%Y") + "\n"
        except:
            data = ""
        try:
            doc_index = "№" + str(conversation["document"]["fields"]["documentNumber"])
            if data == "":
                doc_index += "\n"
        except:
            doc_index = ""
        try:
            doc_key = str(conversation["document"]["type"])
            metaurl = f'https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_code)}/documentTypes/{doc_key}'
            meta_response = requests.get(metaurl, headers=headers)
            try:
                doc_name = meta_response.json()["titles"]["ru"] + " "
            except:
                try:
                    doc_name = meta_response.json()["title"] + " "
                except:
                    doc_name = meta_response.json()["titles"]["en"] + " "
            other_fields = ""
            try:
                # meta_fields = meta_response.json()["fields"]
                for field in meta_response.json()["fields"]:
                    if field["formProperties"]["form"]["visible"] and (
                            field["key"] not in ["sumTotal", "currency", "contractor", "documentDate",
                                                 "documentNumber"]):
                        try:
                            other_fields += field["component"]["label"] + ": " + str(
                                conversation["document"]["fields"][field["key"]])
                        except:
                            other_fields += field["component"]["labels"]["ru"] + ": " + str(
                                conversation["document"]["fields"][field["key"]]) + "\n"
                        print(other_fields)
            except:
                pass
        except:
            doc_name = ""

        stage = "\n\n" + f"<i>Завершено</i>"
        for stage_type in response_types_list:
            try:
                if stage_type["type"] == conversation["document"]['flowStageType']:
                    stage = "\n\n" + f"<i>{stage_type['name']}</i>"
            except:
                stage = ""
        try:
            comment = "\n\n" + conversation["task"]["description"]
        except:
            comment = ""

        try:
            author = "\n" + "От кого: " + conversation["task"]["author"]["name"] + " " + conversation["task"]["author"][
                "surname"]
        except:
            author = ""
        messages[conversation["document"]["oguid"]].append(comment + author)

        result[conversation["document"]["oguid"]] = (cost,
                                                     org__name,
                                                     data,
                                                     doc_index,
                                                     doc_name,
                                                     other_fields,
                                                     messages,
                                                     stage,
                                                     conversation["task"]["oguid"],
                                                     conversation["task"]["author"]["oguid"]
                                                     )  # Найти какие данные нужно вытащить из тасков
    return result


async def post_message_answer(p_access, p_refresh, org_id, entity_id, user_og_id, answer):
    headers = {"Access-Token": f"{p_access}", 'content-type': 'application/json'}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/flows/entities/{entity_id}/tasks"

    json = {
        'assignedToUserOguid': user_og_id,
        "description": answer
    }

    response = requests.post(url, headers=headers, json=json)
    while response.status_code != 201:
        await get_access(p_refresh)
        response = requests.post(url, headers=headers, json=json)

    return "SUCCESS"