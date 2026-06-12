import motor.motor_asyncio
import asyncio

async def check():
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['football_unified']
    collections = ['competitions', 'seasons', 'teams', 'players', 'matches', 'source_links', 'transformation_runs', 'player_match_stats', 'team_match_stats']
    for coll in collections:
        count = await db[coll].count_documents({})
        print(f'{coll.capitalize()}: {count}')
if __name__ == '__main__':
    asyncio.run(check())