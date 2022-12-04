from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from threading import Semaphore
import time

max_tasks = 5
queue = Queue()
semaphore = Semaphore()

def count(num: int):
    print(f"One: {num}")
    time.sleep(max_tasks - num + 1)
    print(f"Two: {num}")
    with semaphore:
        queue.put_nowait(num)

pool = ThreadPoolExecutor()

results: list[int] = []
s = time.perf_counter()
futures = [pool.submit(count, i + 1) for i in range(max_tasks)]
print('All tasks submitted')

while True:
    with semaphore:
        try:
            result = queue.get_nowait()
        except Empty:
            print('Waiting...')
        else:
            if result:
                results.append(result)
                print(f'Got: {result}')
            if all(future.done() for future in futures):
                print('All tasks complete')
                break

    time.sleep(0.01)

print(results)

elapsed = time.perf_counter() - s
print(f"{__file__} executed in {elapsed:0.2f} seconds.")
