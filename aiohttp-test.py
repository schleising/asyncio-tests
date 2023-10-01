import asyncio
import re
import aiohttp
import logging
import time
from types import SimpleNamespace

from rich.logging import RichHandler
from rich.progress import track, Progress

# Log the start of the aiohttp request
async def on_request_start(session: aiohttp.ClientSession, trace_config_ctx: SimpleNamespace, params: aiohttp.TraceRequestStartParams) -> None:
    # Log the request in blue
    log.debug(f"[dodger_blue1]Starting request[/] {params.url}")

# Log the end of the aiohttp request
async def on_request_end(session: aiohttp.ClientSession, trace_config_ctx: SimpleNamespace, params: aiohttp.TraceRequestEndParams) -> None:
    # Log the request in red
    log.debug(f"[green]Finished request[/] {params.url}")

async def load_links_sequentially(session: aiohttp.ClientSession, links: list) -> float:
    # Start a timer
    start = time.perf_counter()

    # Load the links sequentially
    for link in track(links):
        # Load the link
        await load_link(session, link)

    # Stop the timer
    end = time.perf_counter()

    # Calculate the duration
    sequential_duration = end - start

    # Log that we are finished
    logging.debug(f"[steel_blue1]Loading links sequentially finished in {sequential_duration} seconds[/]")

    # Return the duration
    return sequential_duration

async def load_links_asynchronously(session: aiohttp.ClientSession, links: list) -> float:
    # Start a timer
    start = time.perf_counter()

    with Progress() as progress:
        # Add coroutines to load the links asynchronously
        coroutines = [load_link(session, link, progress) for link in links]

        # Create a task to track the progress
        task = progress.add_task("Working...", total=len(links))

        # Wait for all tasks to finish
        await asyncio.gather(*coroutines)

        # Update the progress
        progress.update(task, completed=len(links))

    # Stop the timer
    end = time.perf_counter()

    # Calculate the duration
    async_duration = end - start

    # Log that we are finished
    logging.debug(f"[steel_blue1]Loading links asynchronously finished in {async_duration} seconds[/]")

    # Return the duration
    return async_duration

# Function to load a link
async def load_link(session, link, progress: Progress | None = None) -> None:
    # Send a request
    async with session.get(link) as response:
        # Check the status code
        if response.status == 200:
            # Get the response text, this actually loads the link
            await response.text()
        else:
            # Print the status code
            logging.error(f"Status code {response.status} for {link}")

    # Update the progress
    if progress is not None:
        progress.advance(progress.tasks[0].id, 1)

async def main():
    # Create a regex to find links to theguardian.com
    regex = re.compile(r"https://www\.bbc\.com/[a-z0-9\-\/]+")

    # Create a trace config
    trace_config = aiohttp.TraceConfig()

    # Add our loggers to the trace config
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)

    # Create a session
    async with aiohttp.ClientSession(trace_configs=[trace_config]) as session:
        # Create a request
        async with session.get("https://www.bbc.com") as response:
            # Get the response text
            response_text = await response.text()

        # Find all links
        links = regex.findall(response_text)

        # Log that we are loading the links with a nice decoration
        logging.debug("[red]==============================[/]")
        logging.info("[steel_blue1]Loading links sequentially[/]")

        # Load the links sequentially
        sequential_duration = await load_links_sequentially(session, links)

        # Log that we are loading the links asynchronously
        logging.debug("[red]==============================[/]")
        logging.info("[steel_blue1]Loading links asynchronously[/]")

        # Load the links asynchronously
        async_duration = await load_links_asynchronously(session, links)

        # Log that we are finished with a nice decoration
        logging.debug("[red]==============================[/]")

        # Log the sequential duration again
        logging.info(f"[steel_blue1]Loading links sequentially finished in   {sequential_duration:.3f} seconds[/]")

        # Log that we are finished
        logging.info(f"[steel_blue1]Loading links asynchronously finished in {async_duration:.3f} seconds[/]")

        # Log the speedup
        logging.info(f"[steel_blue1]Speedup Percentage: {round((sequential_duration - async_duration) / sequential_duration * 100, 2)}%[/]")

if __name__ == "__main__":
    # Change the logging level to DEBUG to see the aiohttp request logs
    logging.basicConfig(
        level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[RichHandler(markup=True)]
    )

    # Get the logger
    log = logging.getLogger("rich")

    # Run the main function
    asyncio.run(main())
