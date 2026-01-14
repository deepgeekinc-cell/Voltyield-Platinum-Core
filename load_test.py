import asyncio
import httpx

URL = "http://127.0.0.1:8080/ingest/"

async def main():
    print("🚀 GENERATING TRANS-ATLANTIC YIELD ($5.3M Simulation)...")
    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(20):
            payload = {
                "batch_id": f"AMZN-UNIT-{i}",
                "region": "US",
                "asset_cost": 250000.00, 
                "is_heavy_duty": True,
                "qualified_zone": True,
                "data": [{"sensor": "integrity", "value": 1.0}]
            }
            tasks.append(client.post(URL, json=payload))
        await asyncio.gather(*tasks)
    print("✅ GLOBAL YIELD MAXIMIZED AND INKED.")

if __name__ == "__main__":
    asyncio.run(main())
