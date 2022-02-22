def normal():
    print('hi')


import asyncio

# valueerror: expected coro, got None
asyncio.run(normal())

