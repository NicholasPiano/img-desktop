import asyncio, pythrust

loop = asyncio.get_event_loop()
api = pythrust.API(loop)

asyncio.async(api.spawn())
asyncio.async(api.window({ 'root_url': 'http://arkaeologic.pythonanywhere.com' }).show())

loop.run_forever()
