from typing import Dict
from collections import defaultdict

import requests
import datetime

from database import ActiveUsers
from bot import MyBot


async def sign_in(login, password) -> (str, str):
    headers = {'content-type': 'application/json'}
    data = {
        "email": login,
        "password": password
    }
    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/signin"

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        return False
    else:
        access = response.json()["access"]
        refresh = response.json()["refresh"]

        return access["value"], refresh["value"]


async def get_user_oguid(access_token, refresh_token, user_id) -> str:
    headers = {"Access-Token": f"{access_token}"}

    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/user"

    response = requests.get(url, headers=headers)
    user_oguid = response.json()["oguid"]

    while response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
        response = requests.post(url, headers=headers)
        user_oguid = response.json()["oguid"]

    return user_oguid


async def get_access(refresh_token, user_id) -> str:
    headers = {'content-type': 'application/json'}
    data = {
        "value": f"{refresh_token}",
    }
    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/token-refresh"

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        data = (await ActiveUsers.filter(user_id=user_id).values_list("login", "password"))[0]
        tokens = await sign_in(login=data[0], password=data[1])
        await ActiveUsers.filter(user_id=user_id).update(refresh_token=tokens[1])
        return tokens[0]
    else:
        access = response.json()["access"]
        return access["value"]


async def get_orgs_dict(access_token, refresh_token, user_id) -> dict:
    headers = {"Access-Token": f"{access_token}"}
    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/user"

    response = requests.get(url, headers=headers)

    orgs = response.json()["orgs"]
    result = {}
    ctr = 1
    for org in orgs:
        result[f"{ctr}"] = (org["name"], org["oguid"])
        ctr += 1

    while response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
        response = requests.get(url, headers=headers)

    return result


async def get_tasks_dict(access_token, refresh_token, user_id, org_id) -> dict:
    headers = {"Access-Token": f"{access_token}", "Accept-Language": "ru"}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/flows/tasks"

    params = {
        'showMode': "NEED_TO_ACTION",
        'isCompleted': "false"
    }

    response = requests.get(url, headers=headers, params=params)
    while response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
        response = requests.get(url, headers=headers, params=params)

    types_headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json', "Accept-Language": "ru"}
    types_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/routes/flowStageTypes"
    response_types = requests.get(types_url, headers=types_headers, params=params)

    response_types_list = response_types.json()
    while response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
        response = requests.get(url, headers=headers, params=params)

    tasks = response.json()
    result = {}
    ctr = 0
    for task in tasks:
        try:
            cost = "Сумма: " + str(task["document"]["fields"]["sumTotal"]) + " " + str(
                task["document"]["fields"]["currency"]) + "\n "
        except KeyError:
            cost = ""
        try:
            org__name = task["document"]["fields"]["contractor"] + "\n"
        except KeyError:
            org__name = ""
        try:
            data = " От " + datetime.datetime.fromtimestamp(
                task["document"]["fields"]["documentDate"] / 1e3).strftime("%d.%m.%Y") + "\n"
        except KeyError:
            data = ""
        try:
            doc_index = "№" + str(task["document"]["fields"]["documentNumber"])
            if data == "":
                doc_index += "\n"
        except KeyError:
            doc_index = ""
        try:
            doc_key = str(task["document"]["type"])
            meta_url = f'https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/documentTypes/{doc_key}'
            meta_response = requests.get(meta_url, headers=headers)
            try:
                doc_name = meta_response.json()["titles"]["ru"]
            except KeyError:
                try:
                    doc_name = meta_response.json()["title"]
                except KeyError:
                    doc_name = meta_response.json()["titles"]["en"]
            other_fields = ""
            try:
                for field in meta_response.json()["fields"]:
                    if field["formProperties"]["form"]["visible"] and (
                            field["key"] not in ["sumTotal", "currency", "contractor", "documentDate",
                                                 "documentNumber"]):
                        try:
                            other_fields += field["component"]["label"] + ": " + str(
                                task["document"]["fields"][field["key"]])
                        except KeyError:
                            other_fields += field["component"]["labels"]["ru"] + ": " + str(
                                task["document"]["fields"][field["key"]]) + "\n"
                        print(other_fields)
            except KeyError:
                pass
        except KeyError:
            doc_name = ""
        stage = "\n\n" + f"<i>Завершено</i>"
        for stage_type in response_types_list:
            try:
                if stage_type["type"] == task["document"]['flowStageType']:
                    stage = "\n\n" + f"<i>{stage_type['name']}</i>"
            except KeyError:
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


async def get_doc_dict(access_token, refresh_token, org_id, doc_id, user_id, page):
    headers = {"Access-Token": f"{access_token}"}

    page_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/documents/{doc_id}/page/{page}"
    page_response = requests.get(page_url, headers=headers)
    while page_response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
    len = page_response.headers.get("X-Total-Pages")
    binary_img = page_response.text

    doc_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/documents/{doc_id}"
    doc_response = requests.get(doc_url, headers=headers)
    while doc_response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
    doc_response_json = doc_response.json()

    try:
        doc_task_id = doc_response_json["tasks"][0]["oguid"]
        doc_task_type = doc_response_json["tasks"][0]["type"]
    except:  # ругается на то что IndexError: list index out of range если нет задач по файлу
        doc_task_id = ""
        doc_task_type = ""

    try:
        doc_att_id = doc_response_json["documentAttachmentOguid"]
    except KeyError:
        doc_att_id = ""

    task_type_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/routes/flowStageTypes"
    headers = {"Access-Token": f"{access_token}", "Accept-Language": "ru"}
    type_response = requests.get(task_type_url, headers=headers)
    while type_response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
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


async def get_doc_dict(access_token, refresh_token, org_id, doc_id, user_id, page):
    headers = {"Access-Token": f"{access_token}"}

    page_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/documents/{doc_id}/page/{page}"
    page_response = requests.get(page_url, headers=headers)
    while page_response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
    len = page_response.headers.get("X-Total-Pages")  # Этот ******* запрос теперь нужен только чтобы узнать длинну
    # документа, при этом её больше особо ниоткуда не вытащишь
    # *****************, я в шоке

    doc_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/documents/{doc_id}"
    doc_response = requests.get(doc_url, headers=headers)
    while doc_response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
    doc_response_json = doc_response.json()

    try:
        doc_task_id = doc_response_json["tasks"][0]["oguid"]
        doc_task_type = doc_response_json["tasks"][0]["type"]
    except:  # ругается на то что IndexError: list index out of range если нет задач по файлу
        doc_task_id = ""
        doc_task_type = ""

    try:
        doc_att_id = doc_response_json["documentAttachmentOguid"]
    except KeyError:
        doc_att_id = ""

    task_type_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/routes/flowStageTypes"
    headers = {"Access-Token": f"{access_token}", "Accept-Language": "ru"}
    type_response = requests.get(task_type_url, headers=headers)
    while type_response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
    types_response_json = type_response.json()
    doc_task_name = ""
    for type in types_response_json:
        if type["type"] == doc_task_type:
            doc_task_name = type["buttonCaption"]

    return {"len": len,
            "task_id": doc_task_id,
            "task_type": doc_task_name,
            "task_type_service": doc_task_type,
            "doc_att_id": doc_att_id}


async def post_doc_action(access_token, refresh_token, org_id, task_id, action, user_id):
    headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/flows/tasks/{task_id}/complete"
    action_response = requests.post(url, headers=headers, json={"result": action})

    while (action_response.status_code == 400) or (action_response.status_code == 500):
        await get_access(refresh_token=refresh_token, user_id=user_id)
        action_response = requests.post(url, headers=headers, json={"result": action})

    if action_response.status_code == 409:
        for error in action_response.json():
            MyBot.bot.send_message(user_id, error["errorMessage"])


async def get_certificate(access_token, refresh_token, org_id, user_oguid, user_id):
    headers = {"Access-Token": f"{access_token}"}
    certif_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/users/{user_oguid}/certificate"
    certif_response = requests.get(certif_url, headers=headers)
    while certif_response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
        certif_response = requests.get(certif_url, headers=headers)
    try:
        certif_id = certif_response.json()["oguid"]
        certif_standard = certif_response.json()["standard"]
    except KeyError:
        certif_id = ""
        certif_standard = ""
    return certif_id, certif_standard


async def post_hash(access_token, refresh_token, org_id, standard, att_doc_id, user_id):
    headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
    hash_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/attachments/hash"
    data = {"standard": standard,
            "attachmentOguid": att_doc_id}

    hash_response = requests.post(hash_url, headers=headers, json=data)
    while hash_response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
        hash_response = requests.post(hash_url, headers=headers, json=data)
    try:
        hash = hash_response.json()["hash"]
    except KeyError:
        hash = ""
    return hash


async def post_doc_sign(access_token, refresh_token, org_id, user_oguid, user_id, att_doc_id, doc_id):
    certif = await get_certificate(access_token=access_token,
                                   refresh_token=refresh_token,
                                   org_id=org_id,
                                   user_oguid=user_oguid,
                                   user_id=user_id)
    certif_id, certif_stand = certif[0], certif[1]
    if certif_id == "":
        return "ERROR"

    hash = await post_hash(access_token=access_token,
                           refresh_token=refresh_token,
                           org_id=org_id,
                           standard=certif_stand,
                           att_doc_id=att_doc_id,
                           user_id=user_id)
    if hash == "":
        return "ERROR"

    headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
    sign_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/users/{user_oguid}/docuForceCertificate/{certif_id}/sign"
    sign_data = {"hash": hash}
    action_response = requests.post(sign_url, headers=headers, json=sign_data)

    while action_response.status_code != 201:
        await get_access(refresh_token=refresh_token, user_id=user_id)
        action_response = requests.post(sign_url, headers=headers, json=sign_data)

    add_sign_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/documents/{doc_id}/attachments/signatures"
    add_sign_data = {"oguid": action_response.text[1:-1],
                     "comment": ""}
    add_sign_response = requests.post(add_sign_url, headers=headers, json=add_sign_data)

    print(add_sign_response)
    return "SUCCESS"


async def get_doc_list(access_token, refresh_token, org_id, user_id, contained_string=""):
    headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/documents"

    if contained_string == "":
        params = {}
    else:
        params = {"query.like": contained_string}

    response = requests.get(url, headers=headers, params=params)
    while response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
        response = requests.get(url, headers=headers, params=params)

    types_headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json', "Accept-Language": "ru"}
    types_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/routes/flowStageTypes"

    response_types = requests.get(types_url, headers=types_headers, params=params)
    while response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
        response_types = requests.get(types_url, headers=types_headers, params=params)

    result = []
    resp_list = response.json()
    response_types_list = response_types.json()
    for resp in resp_list:
        try:
            cost = "Сумма: " + str(resp["fields"]["sumTotal"]) + " " + str(
                resp["fields"]["currency"]) + "\n"
        except KeyError:
            cost = ""
        try:
            org__name = resp["fields"]["contractor"] + "\n"
        except KeyError:
            org__name = ""
        try:
            data = " От " + datetime.datetime.fromtimestamp(
                resp["fields"]["documentDate"] / 1e3).strftime("%d.%m.%Y") + "\n"
        except:  # Если его нет то он не разделится на 1е3
            data = ""
        try:
            doc_index = "№" + str(resp["fields"]["documentNumber"])
            if data == "":
                doc_index += "\n"
        except KeyError:
            doc_index = ""
        try:
            doc_key = str(resp["type"])
            metaurl = f'https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/documentTypes/{doc_key}'
            meta_response = requests.get(metaurl, headers=headers)
            try:
                doc_name = meta_response.json()["titles"]["ru"]
            except KeyError:
                try:
                    doc_name = meta_response.json()["title"]
                except KeyError:
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
                        except KeyError:
                            other_fields += field["component"]["labels"]["ru"] + ": " + str(
                                resp["fields"][field["key"]]) + "\n"
                        print(other_fields)
            except KeyError:
                pass
        except KeyError:
            pass

        try:
            doc_id = resp["oguid"]
        except KeyError:
            doc_id = ""

        stage = "\n\n" + f"<i>Завершено</i>"
        for stage_type in response_types_list:
            try:
                if stage_type["type"] == resp['flowStageType']:
                    stage = "\n\n" + f"<i>{stage_type['name']}</i>"
            except KeyError:
                stage = ""

        result.append((cost, org__name, data, doc_index, doc_name, doc_id, other_fields, stage))

    return result


async def get_messages_dict(access_token, refresh_token, org_id, user_id):
    headers = {"Access-Token": f"{access_token}", "Accept-Language": "ru"}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/flows/tasks"

    params = {'showMode': "TODOS_ONLY",
              'isCompleted': "false"}

    response = requests.get(url, headers=headers, params=params)
    while response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
        response = requests.get(url, headers=headers, params=params)

    types_headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json', "Accept-Language": "ru"}
    types_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/routes/flowStageTypes"
    response_types = requests.get(types_url, headers=types_headers, params=params)

    response_types_list = response_types.json()
    conversations = response.json()

    result = {}
    messages = defaultdict(list)
    for conversation in conversations:
        try:
            cost = "Сумма: " + str(conversation["document"]["fields"]["sumTotal"]) + " " + str(
                conversation["document"]["fields"]["currency"])
        except KeyError:
            cost = ""
        try:
            org__name = conversation["document"]["fields"]["contractor"] + "\n"
        except KeyError:
            org__name = ""
        try:
            data = " От " + datetime.datetime.fromtimestamp(
                conversation["document"]["fields"]["documentDate"] / 1e3).strftime("%d.%m.%Y") + "\n"
        except KeyError:
            data = ""
        try:
            doc_index = "№" + str(conversation["document"]["fields"]["documentNumber"])
            if data == "":
                doc_index += "\n"
        except KeyError:
            doc_index = ""
        try:
            doc_key = str(conversation["document"]["type"])
            metaurl = f'https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/documentTypes/{doc_key}'
            meta_response = requests.get(metaurl, headers=headers)
            try:
                doc_name = meta_response.json()["titles"]["ru"] + " "
            except KeyError:
                try:
                    doc_name = meta_response.json()["title"] + " "
                except KeyError:
                    doc_name = meta_response.json()["titles"]["en"] + " "
            other_fields = ""
            try:
                for field in meta_response.json()["fields"]:
                    if field["formProperties"]["form"]["visible"] and (
                            field["key"] not in ["sumTotal", "currency", "contractor", "documentDate",
                                                 "documentNumber"]):
                        try:
                            other_fields += field["component"]["label"] + ": " + str(
                                conversation["document"]["fields"][field["key"]])
                        except KeyError:
                            other_fields += field["component"]["labels"]["ru"] + ": " + str(
                                conversation["document"]["fields"][field["key"]]) + "\n"
                        print(other_fields)
            except KeyError:
                pass
        except KeyError:
            doc_name = ""

        stage = "\n\n" + f"<i>Завершено</i>"
        for stage_type in response_types_list:
            try:
                if stage_type["type"] == conversation["document"]['flowStageType']:
                    stage = "\n\n" + f"<i>{stage_type['name']}</i>"
            except KeyError:
                stage = ""
        try:
            comment = "\n\n" + conversation["task"]["description"]
        except KeyError:
            comment = ""

        try:
            author = "\n" + "От кого: " + conversation["task"]["author"]["name"] + " " + conversation["task"]["author"][
                "surname"]
        except KeyError:
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


async def post_message_answer(access_token, refresh_token, org_id, entity_id, user_oguid, user_id, answer):
    headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/flows/entities/{entity_id}/tasks"

    json = {
        'assignedToUserOguid': user_oguid,
        "description": answer
    }

    response = requests.post(url, headers=headers, json=json)
    while response.status_code != 201:
        await get_access(refresh_token=refresh_token, user_id=user_id)
        response = requests.post(url, headers=headers, json=json)

    return "SUCCESS"


async def get_file(p_access, p_refresh, org_code, doc_att_id):
    headers = {"Access-Token": f"{p_access}"}
    download_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_code}/attachments/{doc_att_id}/file"
    download_response = requests.get(download_url, headers=headers)
    while download_response.status_code != 200:
        await get_access(p_refresh)
        download_response = requests.get(download_url, headers=headers)
    download_response_content = download_response.content
    download_response_title = download_response.headers.get("content-disposition")[22:-1]
    return {"file_title": download_response_title,
            "file_content_bytes": download_response_content}
