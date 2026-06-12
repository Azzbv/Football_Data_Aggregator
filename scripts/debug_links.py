import motor.motor_asyncio
import asyncio

async def check():
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['football_unified']
    count = await db['source_links'].count_documents({'source_name': 'statsbomb', 'entity_type': 'match'})
    print(f'Match Links (StatsBomb): {count}')
    link = await db['source_links'].find_one({'source_name': 'statsbomb', 'entity_type': 'match'})
    if link:
        print(f'Example Link: {link}')
if __name__ == '__main__':
    asyncio.run(check())