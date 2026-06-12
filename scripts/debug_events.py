import motor.motor_asyncio
import asyncio

async def check():
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['statsbomb_raw']
    event = await db['events'].find_one()
    if event:
        print(f"Match ID type: {type(event.get('match_id'))}")
        print(f"Match ID value: {event.get('match_id')}")
    else:
        print('No events found')
if __name__ == '__main__':
    asyncio.run(check())