"""
This file tests the run_in_thread_pool_executor function.
It creates four tasks that calculate the fibonacchi number for a given input.
The tasks are run in separate threads and the results are sent to a queue.
The main thread then gets the results from the queue and prints them.

As Python is single threaded, this is not a true parallel solution,
therefore, even though the tasks are run in separate threads, they will not be run in parallel
and will take longer to complete than if they were run in parallel on separate CPUs.

However, the tasks don't block the main thread, so the main thread can continue to do other things, like getting the results from the queue.

See https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor for more information on the run_in_executor function.

See run_in_process_pool_executor_test.py for a test of the run_in_process_pool_executor function which is a true parallel solution.
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import threading
import queue

def fibonacchi(n: int) -> int:
    # Calculate the fibonacchi number for n
    if n < 2:
        # If n is less than 2, return n
        return n
    else:
        # Otherwise, return the sum of the previous two fibonacchi numbers
        return fibonacchi(n-1) + fibonacchi(n-2)

def print_num(task_id: int, thread_queue: queue.Queue, stop_event: threading.Event) -> None:
    # Calculate the input for the fibonacchi function
    input: int = 33 + task_id

    # Print that the task has started
    print(f"Task {task_id} started")

    # Run the task until the stop_event is set
    while not stop_event.is_set():
        # Start a timer
        start = time.perf_counter()

        # Calculate fibonacchi number for input
        output = fibonacchi(input)

        # Stop timer
        end = time.perf_counter()

        # Calculate duration
        duration = end - start

        # Print result and duration
        print(f"Task {task_id} input: {input}, output: {output}, duration: {duration}")

        # Send result to queue
        thread_queue.put_nowait({'Task ID': task_id, 'Input': input, 'Output': output})

    print(f"Task {task_id} stopped")

async def main():
    # Get the current event loop
    loop = asyncio.get_running_loop()

    # Create a queue that we will use to get our results
    thread_queue = queue.Queue()

    # Create an event that we will use to stop our tasks
    stop_event = threading.Event()

    # Create a thread pool executor
    with ThreadPoolExecutor() as pool:
        # Create threads to run our blocking tasks
        thread1 = loop.run_in_executor(pool, print_num, 1, thread_queue, stop_event)
        thread2 = loop.run_in_executor(pool, print_num, 2, thread_queue, stop_event)
        thread3 = loop.run_in_executor(pool, print_num, 3, thread_queue, stop_event)
        thread4 = loop.run_in_executor(pool, print_num, 4, thread_queue, stop_event)

        while True:
            try:
                # Get result from queue
                result = thread_queue.get_nowait()

                # Print result
                print(result)
            except queue.Empty:
                try:
                    # Sleep for 0.1 second 
                    await asyncio.sleep(0.1)
                except asyncio.CancelledError:
                    # Set the stop event
                    print('Settting stop event')
                    stop_event.set()

                    # Wait for threads to finish
                    print('Waiting for threads to finish')
                    await asyncio.gather(thread1, thread2, thread3, thread4, return_exceptions=True)

                    # Print that the threads are finished
                    print('Threads finished')

                    # Break out of the loop
                    break

    # Print that the main thread is finished
    print('Main thread finished')


if __name__ == "__main__":
    asyncio.run(main(), debug=False)
