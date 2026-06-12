import motor.motor_asyncio
import asyncio
import uuid
from transform.mapping.name_normalizer import NameNormalizer

async def debug():
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['football_unified']
    normalizer = NameNormalizer()
    name = 'Real Madrid CF'
    norm = normalizer.normalize(name)
    print(f'Name: {name} -> Norm: {norm}')
    await db['teams'].delete_many({})
    u_id = f'team-{uuid.uuid4().hex[:8]}'
    await db['teams'].insert_one({'unified_id': u_id, 'name': name, 'normalized_name': norm})
    print(f'Inserted: {u_id}')
    found = await db['teams'].find_one({'normalized_name': norm})
    print(f"Found: {(found.get('unified_id') if found else 'NOT FOUND')}")
    norm_2 = normalizer.normalize('real madrid')
    print(f'Norm 2: {norm_2}')
    found_2 = await db['teams'].find_one({'normalized_name': norm_2})
    print(f"Found 2: {(found_2.get('unified_id') if found_2 else 'NOT FOUND')}")
if __name__ == '__main__':
    asyncio.run(debug())