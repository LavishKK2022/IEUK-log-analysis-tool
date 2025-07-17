import json
import os
import re
from pprint import pprint
import typer
from typing_extensions import Annotated
from collections import (
    defaultdict,
    Counter
)

# Parameters
IP = defaultdict(lambda: defaultdict(list))
ENDPOINT = defaultdict(lambda: defaultdict(list))
RESULTS = 'results.json'
LOG_FILE = 'sample-log.log'


def format(
        table: defaultdict
) -> dict:
    """
    Ensures the tables store the counts of every IP address.

    Args:
        table (defaultdict): The table to format.

    Returns:
        dict: Formatted table.
    """
    temp = {}
    for key, value in table.items():
        inner_temp = {}
        for field, lst in value.items():
            inner_temp[field] = list(Counter(lst).items())
        temp[key] = inner_temp
    return temp


def store(
        path: str
) -> None:
    """
    Stores the tables under 'RESULTS' JSON file.

    Args:
        path (str): The path to the results file.
    """
    global IP, ENDPOINT
    storage = {
        'IP': format(IP),
        'ENDPOINT': format(ENDPOINT)
    }
    with open(path, 'w') as file:
        json.dump(storage, file)


def retrieve(
        path: str
) -> None:
    """
    Retrieves the stored JSON file for faster future
    processing.

    Args:
        path (str): The path to the 'RESULTS' file.
    """
    global IP, ENDPOINT
    with open(path, 'r') as file:
        result = json.load(file)
        IP = result['IP']
        ENDPOINT = result['ENDPOINT']


def handle(
        ip: str,
        region: str,
        endpoint: str,
        status: str
) -> None:
    """
    Stores the parameters in the appropriate
    tables.

    Args:
        ip (str): The IP address record.
        region (str): The user region.
        endpoint (str): The endpoint being requested.
        status (str): The return status of the request.
    """
    IP[ip]['region'].append(region)
    IP[ip]['endpoint'].append(endpoint)
    IP[ip]['status'].append(status)
    ENDPOINT[endpoint]['ip'].append(ip)
    ENDPOINT[endpoint]['region'].append(region)
    ENDPOINT[endpoint]['status'].append(status)


def search_table(
        term: str = '',
        limit: int = 10
) -> None:
    """
    Searches the tables to aggregate data based on IP
    or endpoint URI.

    Can limit the number of returned results using the
    'limit' parameter.

    Results are returned in Descending order (from most
    popular to least). They have counts beside them.

    A wildcard search '' is also implemented. This enables
    the retrieval of the data that comprises the report.
    Args:
        term (str, optional): The search term. Defaults to ''.
        limit (int, optional): The number of results. Defaults to 10.
    """
    if not os.path.exists(RESULTS):
        build()
    retrieve(RESULTS)
    result = {}
    if not term:
        endpoints, ips = {}, {}
        for k, v in ENDPOINT.items():
            total = 0
            for _, count in ENDPOINT[k]['ip']:
                total += count
            endpoints[k] = total
        for k, v in IP.items():
            total = 0
            for _, count in IP[k]['endpoint']:
                total += count
            ips[k] = total
        endpoints = list(endpoints.items())
        ips = list(ips.items())
        ips.sort(
            key=lambda x: x[1], reverse=True
        )
        endpoints.sort(
            key=lambda x: x[1], reverse=True
        )
        result['endpoints'] = endpoints[:limit]
        result['ips'] = ips[:limit]
    else:
        table = IP if term in IP else ENDPOINT
        data = table[term]
        for k, v in data.items():
            v.sort(key=lambda x: x[1], reverse=True)
            result[k] = v[:limit]
    pprint(result)


def parse(
        record: str
) -> None:
    """
    Parses the record to retrieve the various components.
    This includes the IP, region, endpoint and status.

    Args:
        record (str): The log record extracted from the
        log file.
    """
    matches = {
        'ip': re.search(
            r"""(^[\d.]*)""",
            record
        ).group(0),
        'region': re.search(
            r"""- ([\S]{2}) -""",
            record
        ).group(1),
        'endpoint': re.search(
            r"""\"(?:POST|GET|PUT|DELETE|OPTIONS|HEAD|PATCH) ([/\w.=%&+?-]*) [\w/.]*\"""",
            record
        ).group(1).split("?")[0],
        'status': re.search(
            r""" ([0-9]*) [0-9]* """,
            record
        ).group(1)
    }
    handle(**matches)


def build(
        path: str = LOG_FILE
) -> None:
    """
    Orchestrates the process of building the
    tables and reading from the file.

    Args:
        path (str, optional): Path to log file. Defaults to LOG_FILE.
    """
    if not os.path.exists(path):
        print('File not found!')
        return

    with open(path, 'r') as file:
        for line in file:
            parse(line.strip())

    store(RESULTS)


def main(
    command: str,
    limit: Annotated[int, typer.Argument()] = 10
) -> None:
    """
    Typer command to provide CLI access.

    Args:
        command (str): The search command to run.
        limit (Annotated[int, typer.Argument, optional): Number of logs to
        fetch. Defaults to 10.
    """
    search_table(command, limit)


if __name__ == "__main__":
    typer.run(main)
