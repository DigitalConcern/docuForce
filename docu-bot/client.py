from typing import Dict
from collections import defaultdict

import httpx
# import await requests
import datetime
from metadata import Metadata
from database import ActiveUsers
from bot import MyBot


async def sign_in(login, password) -> (str, str):
    headers = {'content-type': 'application/json'}
    data = {
        "email": login,
        "password": password
    }
    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/signin"

    async with httpx.AsyncClient(timeout=None) as requests:
        response = await requests.post(url=url, json=data, headers=headers)

    if response.status_code != 200:
        return False
    else:
        access = response.json()["access"]
        refresh = response.json()["refresh"]

        return access["value"], refresh["value"]


async def get_user_oguid(access_token, refresh_token, user_id) -> str:
    headers = {"Access-Token": f"{access_token}"}

    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/user"
    async with httpx.AsyncClient(timeout=None) as requests:
        response = await requests.get(url=url, headers=headers)
    user_oguid = response.json()["oguid"]

    while response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
        async with httpx.AsyncClient(timeout=None) as requests:
            response = await requests.post(url=url, headers=headers)
        user_oguid = response.json()["oguid"]

    return user_oguid


async def get_access(refresh_token, user_id) -> str:
    headers = {'content-type': 'application/json'}
    data = {
        "value": f"{refresh_token}",
    }
    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/token-refresh"
    async with httpx.AsyncClient(timeout=None) as requests:
        response = await requests.post(url=url, json=data, headers=headers)

    if response.status_code != 200:
        data = (await ActiveUsers.filter(user_id=user_id).values_list("login", "password"))[0]
        tokens = await sign_in(login=data[0], password=data[1])
        await ActiveUsers.filter(user_id=user_id).update(refresh_token=tokens[1], access_token=tokens[0])
        return tokens[0]
    else:
        access = response.json()["access"]
        return access["value"]


async def get_orgs_dict(access_token, refresh_token, user_id) -> dict:
    headers = {"Access-Token": f"{access_token}"}
    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/user"
    async with httpx.AsyncClient(timeout=None) as requests:
        response = await requests.get(url=url, headers=headers)

    orgs = response.json()["orgs"]
    result = {}
    ctr = 1
    for org in orgs:
        result[f"{ctr}"] = (org["name"], org["oguid"])
        ctr += 1

    while response.status_code != 200:
        await get_access(refresh_token=refresh_token, user_id=user_id)
        async with httpx.AsyncClient(timeout=None) as requests:
            response = await requests.get(url=url, headers=headers)

    return result


async def get_tasks_dict(access_token, refresh_token, user_id, org_id) -> dict:
    headers = {"Access-Token": f"{access_token}", "Accept-Language": "ru"}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/flows/tasks"

    params = {
        'showMode': "NEED_TO_ACTION",
        'isCompleted': "false",
        'perPage': 100,
    }
    async with httpx.AsyncClient(timeout=None) as requests:
        response = await requests.get(url=url, headers=headers, params=params)
    while response.status_code != 200:
        access_token = await get_access(refresh_token=refresh_token, user_id=user_id)
        headers = {"Access-Token": f"{access_token}", "Accept-Language": "ru"}
        async with httpx.AsyncClient(timeout=None) as requests:
            response = await requests.get(url=url, headers=headers, params=params)

    tasks = response.json()

    result = {}
    ctr = 0

    full_meta_response = (await Metadata.get_meta(user_id=user_id))
    try:
        response_types_list = full_meta_response["flowStageTypes"]
    except:
        response_types_list = {}
    try:
        full_doc_meta_response = full_meta_response["userTypes"]
    except:
        full_doc_meta_response = {}

    for task in tasks:
        try:
            if (task["document"]["fields"]["sumTotal"] is not None) and (
                    task["document"]["fields"]["currency"] is not None):
                cost = "Сумма: " + str(task["document"]["fields"]["sumTotal"]) + " " + str(
                    task["document"]["fields"]["currency"]) + "\n "
            else:
                cost = ""
        except:
            cost = ""
        try:
            org__name = task["document"]["fields"]["contractor"]["nameShort"] + "\n"
        except:
            org__name = ""
        try:
            data = " от " + datetime.datetime.fromtimestamp(
                task["document"]["fields"]["documentDate"] / 1e3).strftime("%d.%m.%Y") + "\n"
        except:
            data = ""
        try:
            if task["document"]["fields"]["documentNumber"] is not None:
                doc_index = "№" + str(task["document"]["fields"]["documentNumber"])
                if data == "":
                    doc_index += "\n"
            else:
                doc_index = ""
        except:
            doc_index = ""

        other_fields_list = []
        other_fields = ""
        try:
            doc_key = str(task["document"]["type"])
            if doc_key not in full_doc_meta_response.keys():
                await Metadata.update_meta(user_id=user_id, access_token=access_token)
                full_doc_meta_response = (await Metadata.get_meta(user_id=user_id))["userTypes"]
            meta_response = full_doc_meta_response[doc_key]
            try:
                doc_name = meta_response["titles"]["ru"]
            except:
                try:
                    doc_name = meta_response["title"]
                except:
                    doc_name = meta_response["titles"]["en"]

            try:
                for field in task["document"]["fields"].keys():
                    if field not in meta_response["fields"].keys():
                        await Metadata.update_meta(user_id=user_id, access_token=access_token)
                        meta_response = (await Metadata.get_meta(user_id=user_id))["userTypes"]
                    if meta_response["fields"][field]["formProperties"]["form"]["visible"] and not \
                            meta_response["fields"][field]["isSystem"] and (
                            field not in ["sumTotal", "currency", "contractor", "documentDate",
                                          "documentNumber"]):
                        field_value = None
                        try:
                            field_value = task["document"]["fields"][field]["value"]
                        except:
                            field_value = task["document"]["fields"][field]

                        if field_value is not None:

                            try:
                                other_fields_list.append(
                                    [meta_response["fields"][field]["formProperties"]["list"]["order"],
                                     meta_response["fields"][field]["component"]["labels"]["ru"] + ": " + str(
                                         field_value)])
                            except:
                                try:
                                    other_fields_list.append(
                                        [meta_response["fields"][field]["formProperties"]["list"]["order"],
                                         meta_response["fields"][field]["component"]["label"] + ": " + str(
                                             field_value)])
                                except:
                                    other_fields_list.append(
                                        [meta_response["fields"][field]["formProperties"]["list"]["order"],
                                         meta_response["fields"][field]["component"]["labels"]["en"] + ": " + str(
                                             field_value)])
                other_fields_list.sort()
                for field, numb in zip(other_fields_list, range(3)):
                    other_fields += field[1]
            except:
                pass
        except:
            doc_name = ""
        stage = f"<b>Завершено</b>\n"
        check_list = []
        for ttype in response_types_list:
            check_list.append(ttype["type"])
        if task["document"]['flowStageType'] not in check_list:
            await Metadata.update_meta(user_id=user_id, access_token=access_token)
            response_types_list = (await Metadata.get_meta(user_id=user_id))["flowStageTypes"]
        for stage_type in response_types_list:
            try:
                if stage_type["type"] == task["document"]['flowStageType']:
                    if task["stage"]["type"] == "SIGNING":
                        stage = "✍🏻 "
                    else:
                        stage = "👌🏻 "
                    stage += f"<b>{stage_type['name']}</b>\n"
                    try:
                        button = stage_type["buttonCaption"]
                        # await get_task_button(doc_task_type=task["document"]['flowStageType'], org_id=org_id,
                        #                                access_token=access_token, refresh_token=refresh_token,
                        #                                user_id=user_id)
                    except:
                        button = ""
            except KeyError:
                pass

        result[f"{ctr}"] = (cost,
                            org__name,
                            data,
                            task["document"]["oguid"],
                            doc_index,
                            doc_name,
                            other_fields,
                            stage,
                            button,
                            task["task"]["type"],
                            task["task"]["oguid"],
                            task["document"]["documentAttachmentOguid"],

                            )  # Найти какие данные нужно вытащить из тасков
        ctr += 1
    return result


async def get_tasks_amount(access_token, refresh_token, user_id, org_id):
    headers = {"Access-Token": f"{access_token}", "Accept-Language": "ru"}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/flows/tasks"

    params = {
        'showMode': "NEED_TO_ACTION",
        'isCompleted': "false",
        'perPage': 100,
    }
    async with httpx.AsyncClient(timeout=None) as requests:
        response = await requests.get(url=url, headers=headers, params=params)
    while response.status_code != 200:
        access_token = await get_access(refresh_token=refresh_token, user_id=user_id)
        headers = {"Access-Token": f"{access_token}", "Accept-Language": "ru"}
        async with httpx.AsyncClient(timeout=None) as requests:
            response = await requests.get(url=url, headers=headers, params=params)

    return len(response.json())


async def get_doc_dict(access_token, refresh_token, org_id, doc_id, user_id, page):
    headers = {"Access-Token": f"{access_token}"}

    page_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/documents/{doc_id}/page/{page}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as requests:
            page_response = await requests.get(url=page_url, headers=headers)
        while page_response.status_code != 200:
            headers = {"Access-Token": f"{await get_access(refresh_token=refresh_token, user_id=user_id)}"}
            async with httpx.AsyncClient(timeout=10.0) as requests:
                page_response = await requests.get(url=page_url, headers=headers)
        len = page_response.headers.get("X-Total-Pages")  # Этот ******* запрос теперь нужен только чтобы узнать длинну
    except:
        len=0
    # документа, при этом её больше особо ниоткуда не вытащишь
    # *****************, я в шоке

    doc_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/documents/{doc_id}"
    async with httpx.AsyncClient(timeout=None) as requests:
        doc_response = await requests.get(url=doc_url, headers=headers)
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
    full_meta_response = (await Metadata.get_meta(user_id=user_id))
    try:
        response_types_list = full_meta_response["flowStageTypes"]
    except:
        response_types_list = {}
    try:
        full_doc_meta_response = full_meta_response["userTypes"]
    except:
        full_doc_meta_response = {}
    # check_list = []
    # for ttype in response_types_list:
    #     check_list.append(ttype["type"])
    # if task["document"]['flowStageType'] not in check_list:
    #     await Metadata.update_meta(user_id=user_id, access_token=access_token)
    task_name = ""
    for button_type in response_types_list:
        if button_type["type"] == doc_task_type:
            task_name = button_type["buttonCaption"]
    try:
        if (doc_response_json["fields"]["sumTotal"] is not None) and (
                doc_response_json["fields"]["currency"] is not None):
            cost = "Сумма: " + str(doc_response_json["fields"]["sumTotal"]) + " " + str(
                doc_response_json["fields"]["currency"]) + "\n"
        else:
            cost = ""
    except:
        cost = ""
    try:
        org__name = doc_response_json["fields"]["contractor"]["nameShort"] + "\n"
    except:
        org__name = ""
    try:
        data = " от " + datetime.datetime.fromtimestamp(
            doc_response_json["fields"]["documentDate"] / 1e3).strftime("%d.%m.%Y") + "\n"
    except:  # Если его нет то он не разделится на 1е3
        data = ""
    try:
        if doc_response_json["fields"]["documentNumber"] is not None:
            doc_index = "№" + str(doc_response_json["fields"]["documentNumber"])
            if data == "":
                doc_index += "\n"
        else:
            doc_index = ""
    except:
        doc_index = ""
    doc_name = ""
    other_fields = ""

    doc_key = str(doc_response_json["type"])
    if doc_key not in full_doc_meta_response.keys():
        await Metadata.update_meta(user_id=user_id, access_token=access_token)
        full_doc_meta_response = (await Metadata.get_meta(user_id=user_id))["userTypes"]
    meta_response = full_doc_meta_response[doc_key]
    try:
        doc_name = meta_response["titles"]["ru"]
    except:
        try:
            doc_name = meta_response["title"]
        except:
            doc_name = meta_response["titles"]["en"]

    try:
        other_fields_list = []
        for field in doc_response_json["fields"].keys():
            if field not in meta_response["fields"].keys():
                await Metadata.update_meta(user_id=user_id, access_token=access_token)
                meta_response = (await Metadata.get_meta(user_id=user_id))["userTypes"]
            if meta_response["fields"][field]["formProperties"]["form"]["visible"] and not \
                    meta_response["fields"][field]["isSystem"] and (
                    field not in ["sumTotal", "currency", "contractor", "documentDate",
                                  "documentNumber"]):
                field_value = None
                try:
                    field_value = doc_response_json["fields"][field]["value"]
                except:
                    field_value = doc_response_json["fields"][field]

                if field_value is not None:
                    try:
                        other_fields_list.append(
                            [meta_response["fields"][field]["formProperties"]["list"]["order"],
                             meta_response["fields"][field]["component"]["labels"]["ru"] + ": " + str(field_value)])
                    except:
                        try:
                            other_fields_list.append(
                                [meta_response["fields"][field]["formProperties"]["list"]["order"],
                                 meta_response["fields"][field]["component"]["label"] + ": " + str(field_value)])
                        except:
                            other_fields_list.append(
                                [meta_response["fields"][field]["formProperties"]["list"]["order"],
                                 meta_response["fields"][field]["component"]["labels"]["en"] + ": " + str(field_value)])
        other_fields_list.sort()
        for field, numb in zip(other_fields_list, range(3)):
            other_fields += field[1]
    except:
        pass
    text = f"{doc_name} {doc_index}{data}{org__name}{cost}{other_fields}"
    return {"len": len,
            "task_id": doc_task_id,
            "task_type": task_name,
            "task_type_service": doc_task_type,
            "doc_att_id": doc_att_id,
            "text": text}


async def post_doc_action(access_token, refresh_token, org_id, task_id, action, user_id):
    headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/flows/tasks/{task_id}/complete"
    async with httpx.AsyncClient(timeout=None) as requests:
        action_response = await requests.post(url=url, headers=headers, json={"result": action})

    while (action_response.status_code == 400) or (action_response.status_code == 500):
        access_token = await get_access(refresh_token=refresh_token, user_id=user_id)
        headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
        async with httpx.AsyncClient(timeout=None) as requests:
            action_response = await requests.post(url=url, headers=headers, json={"result": action})

    if action_response.status_code == 409:
        for error in action_response.json():
            MyBot.bot.send_message(user_id, error["errorMessage"])


async def get_certificate(access_token, refresh_token, org_id, user_oguid, user_id):
    headers = {"Access-Token": f"{access_token}"}
    certif_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/users/{user_oguid}/certificate"
    async with httpx.AsyncClient(timeout=None) as requests:
        certif_response = await requests.get(url=certif_url, headers=headers)

    while certif_response.status_code != 200:
        access_token = await get_access(refresh_token=refresh_token, user_id=user_id)
        headers = {"Access-Token": f"{access_token}"}
        async with httpx.AsyncClient(timeout=None) as requests:
            certif_response = await requests.get(url=certif_url, headers=headers)

    try:
        certif_id = certif_response.json()["oguid"]
        certif_standard = certif_response.json()["standard"]
    except:
        certif_id = ""
        certif_standard = ""
    return certif_id, certif_standard


async def post_hash(access_token, refresh_token, org_id, standard, att_doc_id, user_id):
    headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
    hash_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/attachments/hash"
    data = {"standard": standard,
            "attachmentOguid": att_doc_id}

    async with httpx.AsyncClient(timeout=None) as requests:
        hash_response = await requests.post(url=hash_url, headers=headers, json=data)
    while hash_response.status_code != 200:
        access_token = await get_access(refresh_token=refresh_token, user_id=user_id)
        headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
        async with httpx.AsyncClient(timeout=None) as requests:
            hash_response = await requests.post(url=hash_url, headers=headers, json=data)
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
    async with httpx.AsyncClient(timeout=None) as requests:
        action_response = await requests.post(url=sign_url, headers=headers, json=sign_data)

    while action_response.status_code != 201:
        access_token = await get_access(refresh_token=refresh_token, user_id=user_id)
        headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
        async with httpx.AsyncClient(timeout=None) as requests:
            action_response = await requests.post(url=sign_url, headers=headers, json=sign_data)

    add_sign_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/documents/{doc_id}/attachments/signatures"
    add_sign_data = {"oguid": action_response.text[1:-1],
                     "comment": ""}
    async with httpx.AsyncClient(timeout=None) as requests:
        add_sign_response = await requests.post(url=add_sign_url, headers=headers, json=add_sign_data)

    print(add_sign_response)
    return "SUCCESS"


async def get_doc_list(access_token, refresh_token, org_id, user_id, contained_string=""):
    headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/documents"

    if contained_string == "":
        params = {'perPage': 100}
    else:
        params = {"query.like": contained_string,
                  'perPage': 100, }

    print("request")
    async with httpx.AsyncClient(timeout=None) as requests:
        response = await requests.get(url=url, headers=headers, params=params)
    while response.status_code != 200:
        access_token = await get_access(refresh_token=refresh_token, user_id=user_id)
        headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
        async with httpx.AsyncClient(timeout=None) as requests:
            response = await requests.get(url=url, headers=headers, params=params)
    print("response")

    full_meta_response = (await Metadata.get_meta(user_id=user_id))
    try:
        response_types = full_meta_response["flowStageTypes"]
    except:
        response_types = {}
    try:
        full_doc_meta_response = full_meta_response["userTypes"]
    except:
        full_doc_meta_response = {}

    result = []
    resp_list = response.json()
    response_types_list = response_types
    for resp in resp_list:
        try:
            if (resp["fields"]["sumTotal"] is not None) and (resp["fields"]["currency"] is not None):
                cost = "Сумма: " + str(resp["fields"]["sumTotal"]) + " " + str(
                    resp["fields"]["currency"]) + "\n"
            else:
                cost = ""
        except KeyError:
            cost = ""
        try:
            org__name = resp["fields"]["contractor"]["nameShort"] + "\n"
        except KeyError:
            org__name = ""
        try:
            data = " от " + datetime.datetime.fromtimestamp(
                resp["fields"]["documentDate"] / 1e3).strftime("%d.%m.%Y") + "\n"
        except:  # Если его нет то он не разделится на 1е3
            data = ""
        try:
            if resp["fields"]["documentNumber"] is not None:
                doc_index = "№" + str(resp["fields"]["documentNumber"])
                if data == "":
                    doc_index += "\n"
            else:
                doc_index = ""
        except KeyError:
            doc_index = ""
        try:
            other_fields = ""
            try:
                doc_key = str(resp["type"])
                if doc_key not in full_doc_meta_response.keys():
                    await Metadata.update_meta(user_id=user_id, access_token=access_token)
                    full_doc_meta_response = (await Metadata.get_meta(user_id=user_id))["userTypes"]
                meta_response = full_doc_meta_response[doc_key]
                try:
                    doc_name = meta_response["titles"]["ru"]
                except:
                    try:
                        doc_name = meta_response["title"]
                    except:
                        doc_name = meta_response["titles"]["en"]
                other_fields_list = []
                try:
                    for field in resp["fields"].keys():
                        if field not in meta_response["fields"].keys():
                            await Metadata.update_meta(user_id=user_id, access_token=access_token)
                            meta_response = (await Metadata.get_meta(user_id=user_id))["userTypes"]
                        if meta_response["fields"][field]["formProperties"]["form"]["visible"] and not \
                                meta_response["fields"][field]["isSystem"] and (
                                field not in ["sumTotal", "currency", "contractor", "documentDate",
                                              "documentNumber"]):

                            try:
                                field_value = resp["fields"][field]["value"]
                            except:
                                field_value = resp["fields"][field]
                            if field_value is not None:
                                try:
                                    other_fields_list.append(
                                        [meta_response["fields"][field]["formProperties"]["list"]["order"],
                                         meta_response["fields"][field]["component"]["labels"]["ru"] + ": " + str(
                                             field_value)])
                                except:
                                    try:
                                        other_fields_list.append(
                                            [meta_response["fields"][field]["formProperties"]["list"]["order"],
                                             meta_response["fields"][field]["component"]["label"] + ": " + str(
                                                 field_value)])
                                    except:
                                        other_fields_list.append(
                                            [meta_response["fields"][field]["formProperties"]["list"]["order"],
                                             meta_response["fields"][field]["component"]["labels"]["en"] + ": " + str(
                                                 field_value)])
                    other_fields_list.sort()
                    for field, numb in zip(other_fields_list, range(3)):
                        other_fields += field[1]
                except:
                    pass
            except KeyError:
                pass
        except KeyError:
            pass

        try:
            doc_id = resp["oguid"]
        except KeyError:
            doc_id = ""

        stage = f"<b>Завершено</b>\n"
        for stage_type in response_types_list:
            try:
                if stage_type["type"] == resp['flowStageType']:
                    if resp['flowStageType'] == "SIGNING":
                        stage = "✍🏻"
                    else:
                        stage = "👌🏻"
                    stage += f"<b>{stage_type['name']}</b>\n"
            except KeyError:
                stage = ""

        result.append((cost, org__name, data, doc_index, doc_name, doc_id, other_fields, stage))

    return result


async def get_conversations_dict(access_token, refresh_token, user_id, org_id) -> dict:
    headers = {"Access-Token": f"{access_token}", "Accept-Language": "ru"}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/flows/tasks"

    params = {'showMode': "TODOS_ONLY",
              'isCompleted': "false",
              "page": -1,
              "taskDirection": "TO_ME"}

    async with httpx.AsyncClient(timeout=None) as requests:
        response = await requests.get(url=url, headers=headers, params=params)
    while response.status_code != 200:
        access_token = await get_access(refresh_token=refresh_token, user_id=user_id)
        headers = {"Access-Token": f"{access_token}", "Accept-Language": "ru"}
        async with httpx.AsyncClient(timeout=None) as requests:
            response = await requests.get(url=url, headers=headers, params=params)

    tasks = response.json()
    full_meta_response = (await Metadata.get_meta(user_id=user_id))
    try:
        response_types_list = full_meta_response["flowStageTypes"]
    except:
        response_types_list = {}
    try:
        full_doc_meta_response = full_meta_response["userTypes"]
    except:
        full_doc_meta_response = {}

    result = {}
    ctr = 0
    for task in tasks:
        try:
            if task["document"]["fields"]["sumTotal"] is not None:
                cost = "Сумма: " + str(task["document"]["fields"]["sumTotal"]) + " " + str(
                    task["document"]["fields"]["currency"])
            else:
                cost = ""
        except:
            cost = ""
        try:
            org__name = task["document"]["fields"]["contractor"]["nameShort"] + "\n"
        except:
            org__name = ""
        try:
            data = " от " + datetime.datetime.fromtimestamp(
                task["document"]["fields"]["documentDate"] / 1e3).strftime("%d.%m.%Y") + "\n"
        except:
            data = ""
        try:
            if task["document"]["fields"]["documentNumber"] is not None:
                doc_index = " №" + str(task["document"]["fields"]["documentNumber"])
                if data == "":
                    doc_index += "\n"
            else:
                doc_index = ""
        except:
            doc_index = ""
        other_fields = ""
        other_fields_list = []
        try:
            doc_key = str(task["document"]["type"])
            if doc_key not in full_doc_meta_response.keys():
                await Metadata.update_meta(user_id=user_id, access_token=access_token)
                full_doc_meta_response = (await Metadata.get_meta(user_id=user_id))["userTypes"]
            meta_response = full_doc_meta_response[doc_key]
            try:
                doc_name = meta_response["titles"]["ru"]
            except:
                try:
                    doc_name = meta_response["title"]
                except:
                    doc_name = meta_response["titles"]["en"]

            try:
                for field in task["document"]["fields"].keys():
                    if field not in meta_response["fields"].keys():
                        await Metadata.update_meta(user_id=user_id, access_token=access_token)
                        meta_response = (await Metadata.get_meta(user_id=user_id))["userTypes"]
                    if meta_response["fields"][field]["formProperties"]["form"]["visible"] and not \
                            meta_response["fields"][field]["isSystem"] and (
                            field not in ["sumTotal", "currency", "contractor", "documentDate",
                                          "documentNumber"]):
                        field_value = None
                        try:
                            field_value = task["document"]["fields"][field]["value"]
                        except:
                            field_value = task["document"]["fields"][field]

                        if field_value is not None:

                            try:
                                other_fields_list.append(
                                    [meta_response["fields"][field]["formProperties"]["list"]["order"],
                                     meta_response["fields"][field]["component"]["labels"]["ru"] + ": " + str(
                                         field_value)])
                            except:
                                try:
                                    other_fields_list.append(
                                        [meta_response["fields"][field]["formProperties"]["list"]["order"],
                                         meta_response["fields"][field]["component"]["label"] + ": " + str(
                                             field_value)])
                                except:
                                    other_fields_list.append(
                                        [meta_response["fields"][field]["formProperties"]["list"]["order"],
                                         meta_response["fields"][field]["component"]["labels"]["en"] + ": " + str(
                                             field_value)])
                other_fields_list.sort()
                for field, numb in zip(other_fields_list, range(3)):
                    other_fields += field[1]
            except:
                pass

        #     doc_key = str(task["document"]["type"])
        #     if doc_key not in meta_response.keys():
        #         await Metadata.update_meta(user_id=user_id, access_token=access_token)
        #         meta_response = (await Metadata.get_meta(user_id=user_id))["userTypes"]
        #     meta_response = meta_response[doc_key]
        #     try:
        #         doc_name = meta_response["titles"]["ru"]
        #     except:
        #         try:
        #             doc_name = meta_response["title"]
        #         except:
        #             doc_name = meta_response["titles"]["en"]
        #     other_fields = ""
        #     try:
        #         for field in meta_response["fields"]:
        #             if field["formProperties"]["form"]["visible"] and (
        #                     field["key"] not in ["sumTotal", "currency", "contractor", "documentDate",
        #                                          "documentNumber"]):
        #                 try:
        #                     other_fields += field["component"]["label"] + ": " + str(
        #                         task["document"]["fields"][field["key"]])
        #                 except:
        #                     other_fields += field["component"]["labels"]["ru"] + ": " + str(
        #                         task["document"]["fields"][field["key"]]) + "\n"
        #     except:
        #         pass
        except:
            doc_name = ""
        stage = "\n" + f"Статус: <b>Завершено</b>"
        for stage_type in response_types_list:
            try:
                if stage_type["type"] == task["document"]['flowStageType']:
                    stage = "\n" + f"Статус: <b>{stage_type['name']}</b>"
            except KeyError:
                stage = ""
        try:
            comment = "\n" + task["task"]["description"]
        except KeyError:
            comment = ""

        try:
            author = "\n" + task["task"]["author"]["surname"] + " " + task["task"]["author"]["name"][0] + '.' + \
                     task["task"]["author"]["patronymic"][0]
        except KeyError:
            author = ""
        message = comment
        author_for_resp = task["task"]["author"]["name"] + " " + task["task"]["author"]["surname"]

        result[f"{ctr}"] = (cost,
                            org__name,
                            data,
                            doc_index,
                            doc_name,
                            other_fields,
                            message,
                            stage,
                            task["task"]["oguid"],
                            task["task"]["author"]["oguid"],
                            task["document"]["oguid"],
                            author_for_resp,
                            author
                            )

        ctr += 1
    return result


async def get_conversations_amount(access_token, refresh_token, user_id, org_id):
    headers = {"Access-Token": f"{access_token}", "Accept-Language": "ru"}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{str(org_id)}/flows/tasks"

    params = {'showMode': "TODOS_ONLY",
              'isCompleted': "false",
              "page": -1,
              "taskDirection": "TO_ME"}

    async with httpx.AsyncClient(timeout=None) as requests:
        response = await requests.get(url=url, headers=headers, params=params)
    while response.status_code != 200:
        access_token = await get_access(refresh_token=refresh_token, user_id=user_id)
        headers = {"Access-Token": f"{access_token}", "Accept-Language": "ru"}
        async with httpx.AsyncClient(timeout=None) as requests:
            response = await requests.get(url=url, headers=headers, params=params)

    tasks = response.json()
    return len(tasks)


async def post_markasread(access_token, refresh_token, org_id, task_id, user_id):
    headers = {"Access-Token": f"{access_token}"}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/flows/tasks/{task_id}/markAsRead"

    async with httpx.AsyncClient(timeout=None) as requests:
        response = await requests.post(url=url, headers=headers)
    while response.status_code != 204:
        access_token = await get_access(refresh_token=refresh_token, user_id=user_id)
        headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
        async with httpx.AsyncClient(timeout=None) as requests:
            response = await requests.post(url=url, headers=headers)

    return "NOT CRINGE"


async def post_message_answer(access_token, refresh_token, org_id, entity_id, user_oguid, user_id, answer, task_id):
    headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
    url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/flows/entities/{entity_id}/tasks"

    json = {
        'assignedToUserOguid': user_oguid,
        "description": answer,
        "parentTaskOguid": task_id
    }

    async with httpx.AsyncClient(timeout=None) as requests:
        response = await requests.post(url=url, headers=headers, json=json)
    while response.status_code != 201:
        access_token = await get_access(refresh_token=refresh_token, user_id=user_id)
        headers = {"Access-Token": f"{access_token}", 'content-type': 'application/json'}
        async with httpx.AsyncClient(timeout=None) as requests:
            response = await requests.post(url=url, headers=headers, json=json)
    return "SUCCESS"


async def get_file(access_token, refresh_token, org_id, doc_att_id, user_id):
    headers = {"Access-Token": f"{access_token}"}
    download_url = f"https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/attachments/{doc_att_id}/file"
    async with httpx.AsyncClient(timeout=None) as requests:
        download_response = await requests.get(url=download_url, headers=headers)

    while download_response.status_code != 200:
        access_token = await get_access(refresh_token=refresh_token, user_id=user_id)
        headers = {"Access-Token": f"{access_token}"}
        async with httpx.AsyncClient(timeout=None) as requests:
            download_response = await requests.get(url=download_url, headers=headers)

    download_response_content = download_response.content
    download_response_title = download_response.headers.get("content-disposition")[22:-1]
    return {"file_title": download_response_title,
            "file_content_bytes": download_response_content}