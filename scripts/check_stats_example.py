import motor.motor_asyncio
import asyncio

async def check():
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['football_unified']
    stat = await db['player_match_stats'].find_one({'goals': {'$gt': 0}})
    if stat:
        print(f'Player Match Stat Example: {stat}')
    t_stat = await db['team_match_stats'].find_one()
    if t_stat:
        print(f'Team Match Stat Example: {t_stat}')
if __name__ == '__main__':
    asyncio.run(check())