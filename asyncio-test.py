import asyncio

async def async_range(total: int):
    for i in range(total):
        yield i

async def count(num: int) -> int:
    print(f"One: {num}")
    await asyncio.sleep(1)
    print(f"Two: {num}")

    return num + 3

async def main():
    # result = await asyncio.gather(*(count(i + 1) for i in range(3)))
    result = []
    async for i in async_range(3):
        result.append(count(i))
    print(result)
    print(type(result))

if __name__ == "__main__":
    import time
    s = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
