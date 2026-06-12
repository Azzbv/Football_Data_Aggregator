import motor.motor_asyncio
import asyncio

async def check():
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    match = await client['statsbomb_raw']['matches'].find_one()
    if match:
        print(f"Home Team Keys: {list(match['home_team'].keys())}")
        print(f"Home Team Name: {match['home_team'].get('home_team_name')}")
    else:
        print('No match found')
if __name__ == '__main__':
    asyncio.run(check())