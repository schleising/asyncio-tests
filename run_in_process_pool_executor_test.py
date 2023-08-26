"""
This script tests the run_in_process_pool_executor function.
It creates four tasks that calculate the fibonacchi number for a given input.
The tasks are run in separate processes and the results are sent to a queue.
The main process then gets the results from the queue and prints them.

This is a true parallel solution, as the tasks are run in separate processes on separate CPUs.

See https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor for more information on the run_in_executor function.

See run_in_thread_pool_executor_test.py for a test of the run_in_thread_pool_executor function which is not a true parallel solution.
See to_thread_create_task_test.py for a test of the to_thread function which is not a true parallel solution.
"""

import asyncio
import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from multiprocessing.synchronize import Event as mp_Event
import queue
import signal

def fibonacchi(n: int) -> int:
    # Calculate the fibonacchi number for n
    if n < 2:
        # If n is less than 2, return n
        return n
    else:
        # Otherwise, return the sum of the previous two fibonacchi numbers
        return fibonacchi(n-1) + fibonacchi(n-2)

def print_num(task_id: int, queue: multiprocessing.Queue, stop_event: mp_Event) -> None:
    # Ignore SIGINT
    signal.signal(signal.SIGINT, signal.SIG_IGN)

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
        queue.put_nowait({'Task ID': task_id, 'Input': input, 'Output': output})

    print(f"Task {task_id} stopped")

async def main():
    # Get the event loop
    loop = asyncio.get_running_loop()

    # Create a multiprocessing manager to create a queue and an event
    with multiprocessing.Manager() as manager:
        # Create a queue and an event
        mp_queue = manager.Queue()
        stop_event = manager.Event()

        # Create a process pool
        with ProcessPoolExecutor() as pool:
            # Create processes to run our blocking tasks
            process1 = loop.run_in_executor(pool, print_num, 1, mp_queue, stop_event)
            process2 = loop.run_in_executor(pool, print_num, 2, mp_queue, stop_event)
            process3 = loop.run_in_executor(pool, print_num, 3, mp_queue, stop_event)
            process4 = loop.run_in_executor(pool, print_num, 4, mp_queue, stop_event)

            while True:
                try:
                    # Get result from queue
                    result = mp_queue.get_nowait()

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

                        # Wait for processes to finish
                        print('Waiting for processes to finish')
                        await asyncio.gather(process1, process2, process3, process4, return_exceptions=True)

                        # Print that the processes are finished
                        print('Processes finished')

                        # Break out of the loop
                        break

    # Print that the main process is finished
    print('Main process finished')
            

if __name__ == "__main__":
    asyncio.run(main(), debug=False)
