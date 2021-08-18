import aiohttp

class Requests:

    @staticmethod
    async def get(ses, url:str, **kwargs):
        async with ses.get(url, **kwargs) as r:
            if r.status in range(200, 300):
                data = await r.json()
                return data
    
    @staticmethod
    async def post(ses, url:str, **kwargs):
        async with ses.post(url, **kwargs) as r:
            data = await r.json()
            return data

    @staticmethod
    async def head(ses, url:str, **kwargs):
        async with ses.head(url, **kwargs) as r:
            data = await r.json()
            return data

    @staticmethod
    async def options(ses, url:str, **kwargs):
        async with ses.options(url, **kwargs) as r:
            data = await r.json()
            return data

    @staticmethod
    async def put(ses, url:str, **kwargs):
        async with ses.put(url, **kwargs) as r:
            data = await r.json()
            return data

    @staticmethod
    async def patch(ses, url:str, **kwargs):
        async with ses.patch(url, **kwargs) as r:
            data = await r.json()
            return data

    @staticmethod
    async def delete(ses, url:str, **kwargs):
        async with ses.delete(url, **kwargs) as r:
            data = await r.json()
            return data
