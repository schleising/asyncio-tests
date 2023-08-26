"""
This file contains a test of the create_task function.
It creates four tasks that calculate the fibonacchi number for a given input.
The tasks are run in separate threads and the results are sent to a queue.
The main thread then gets the results from the queue and prints them.

As Python is single threaded, this is not a true parallel solution,
therefore, even though the tasks are run in separate threads, they will not be run in parallel
and will take longer to complete than if they were run in parallel on separate CPUs.

However, the tasks don't block the main thread, so the main thread can continue to do other things, like getting the results from the queue.

See https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread for more information on the to_thread function.
See https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task for more information on the create_task function.
See https://docs.python.org/3/library/asyncio-task.html#task-group for more information on the TaskGroup class.
See https://docs.python.org/3/library/asyncio-task.html#taskgroup-create-task for more information on the TaskGroup.create_task function.

See run_in_process_pool_executor_test.py for a test of the run_in_executor function which is a true parallel solution.
"""

import asyncio
import time

def fibonacchi(n: int) -> int:
    # Calculate the fibonacchi number for n
    if n < 2:
        # If n is less than 2, return n
        return n
    else:
        # Otherwise, return the sum of the previous two fibonacchi numbers
        return fibonacchi(n-1) + fibonacchi(n-2)

def print_num(task_id: int, queue: asyncio.Queue, stop_event: asyncio.Event) -> None:
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
    # Create a queue that we will use to get our results
    queue = asyncio.Queue()

    # Create an event that we will use to stop our tasks
    stop_event = asyncio.Event()

    # Create threads to run our blocking tasks
    thread1 = asyncio.to_thread(print_num, 1, queue, stop_event)
    thread2 = asyncio.to_thread(print_num, 2, queue, stop_event)
    thread3 = asyncio.to_thread(print_num, 3, queue, stop_event)
    thread4 = asyncio.to_thread(print_num, 4, queue, stop_event)

    # Create a task group
    async with asyncio.TaskGroup() as tg:
        # Start our tasks
        tg.create_task(thread1)
        tg.create_task(thread2)
        tg.create_task(thread3)
        tg.create_task(thread4)

        # Print that the tasks are created
        print("jobs created")

        while True:
            try:
                # Try to get an item off the queue, if no items are present continue
                result = queue.get_nowait()

                # Print the result
                print(result)
            except asyncio.QueueEmpty:
                # If the queue is empty, wait for 0.1 seconds and try again
                try:
                    # Wait for 0.1 seconds
                    await asyncio.sleep(0.1)
                except asyncio.CancelledError:
                    # If we get a CancelledError, cancel our tasks and break out of the loop
                    stop_event.set()

                    # Print a message
                    print('Waiting for tasks to finish')

                    # Cancel our tasks (this will be done automatically if we use async with)
                    break

    # Print that the tasks are finished
    print("Tasks finished")

if __name__ == "__main__":
    # Run our main function
    asyncio.run(main(), debug=False)
