from testsite.tornado_main import main as server_main
import asyncio, pythrust

def main():
  loop = asyncio.get_event_loop()
  api = pythrust.API(loop)

  asyncio.async(api.spawn())
  asyncio.async(api.window({ 'root_url': 'http://localhost:8000' }).show())

  loop.run_forever()

if __name__ == '__main__':
  main()
