import asyncio

import motor.motor_asyncio
import httpx

from database import ActiveUsers


class Metadata:
    motor_client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://root:1234@mongo:27017')
    # motor_client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = motor_client['dfbot_cache_db']
    collection = db['dfbot_cache_collection']

    @classmethod
    async def update_meta(cls, user_id: int, access_token):
        # print("Meta DB updated")
        data = (await ActiveUsers.filter(user_id=user_id).values_list("organization"))[0]
        org_id = data[0]

        meta_url_user = f'https://api.docuforce.infologistics.ru/orgs/{str(org_id)}/documents/userTypes'
        meta_url_flow = f'https://api.docuforce.infologistics.ru/orgs/{str(org_id)}/routes/flowStageTypes'

        headers = {"Access-Token": f"{access_token}", "Accept-Language": "ru"}

        async with httpx.AsyncClient() as requests:
            response_user = await requests.get(url=meta_url_user, headers=headers)

        async with httpx.AsyncClient() as requests:
            response_flow = await requests.get(url=meta_url_flow, headers=headers)

        if response_user.status_code != 200 or response_flow.status_code != 200:
            return False

        try:
            await cls.db.collection.insert_one({"_id": user_id,
                                                "flowStageTypes": response_flow.json(),
                                                "userTypes": response_user.json()})
        except:
            await cls.db.collection.update_one({'_id': user_id},
                                               {'$set':
                                                   {
                                                       "flowStageTypes": response_flow.json(),
                                                       "userTypes": response_user.json()
                                                   }
                                               })

        return True

    @classmethod
    async def get_meta(cls, user_id: int):
        # print("Got data from DB")
        return await cls.db.collection.find_one({'_id': user_id})




# asyncio.get_event_loop().run_until_complete(MetadData.update_meta(1234213, 235798))
