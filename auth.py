import json
import requests
from requests import HTTPError


async def sign_in(p_login, p_password) -> (str, str):
    headers = {'content-type': 'application/json'}
    data = {
        "email": p_login,
        "password": p_password
    }
    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/signin"
    try:
        response = requests.post(url, json=data, headers=headers)
        access = response.json()["access"]
        refresh = response.json()["refresh"]

        return access["value"], refresh["value"]

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')


async def get_access(p_refresh) -> str:
    headers = {'content-type': 'application/json'}
    data = {
        "value": f"{p_refresh}",
    }
    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/token-refresh"
    try:
        response = requests.post(url, json=data, headers=headers)
        access = response.json()["access"]

        return access

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')


async def get_orgs_dict(p_access) -> dict:
    headers = {"Access-Token": f"{p_access}"}
    url = "https://im-api.df-backend-dev.dev.info-logistics.eu/user"
    try:
        response = requests.get(url, headers=headers)
        orgs = response.json()["orgs"]
        result = {}

        ctr = 1
        for org in orgs:
            result[f"{ctr}"] = org["name"]
            ctr += 1

        return result

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
