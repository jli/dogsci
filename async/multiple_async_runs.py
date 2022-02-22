async def printhi():
    print('hi')


import asyncio

# this is fine`
asyncio.run(printhi())
asyncio.run(printhi())

async def run_hi():
    asyncio.run(printhi())

asyncio.run(run_hi())
