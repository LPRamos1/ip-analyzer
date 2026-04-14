import sys
from pathlib import Path
import re
import requests
import json
import time
from tabulate import tabulate

# Constants for API limits (45 Requests per minute on IP-API) and Valid extensions
MAX_BATCH_SIZE = 50
RATE_LIMIT_PER_MINUTE = 40
VALID_EXTENSION = [".txt", ".log", ".csv", ".json"]


def validate_input() -> Path:
    """
    Validates command-line arguments and file requirements.

    Checks if the correct number of arguments is provided, if the file
    exists on the system, and if it has a supported extension.

    Returns:
        Path: A pathlib.Path object pointing to the validated file.

    Raises:
        SystemExit: If arguments are invalid, file is missing, or extension is unsupported.
    """
    if len(sys.argv) < 2:
        sys.exit(
            "Too few command-line arguments, use 'python project.py archiveName.txt "
        )
    if len(sys.argv) > 2:
        sys.exit(
            "Too many command-line arguments, use 'python project.py archiveName.txt "
        )
    path = Path(sys.argv[1])
    if not path.is_file():
        sys.exit("File does not exist")
    if path.suffix not in VALID_EXTENSION:
        sys.exit(f"Unsupported file type. Please use: {', '.join(VALID_EXTENSION)}")
    return path


def ip_info(path):
    """
    Orchestrates the extraction process based on file extension.

    Acts as a router, reading the file content and delegating the extraction
    to either JSON-specific or Regex-specific helpers.
    """
    content = path.read_text()
    if path.suffix == ".json":
        return _extract_from_json(content)
    return _extract_from_regex(content)


def _extract_from_regex(text) -> list[str]:
    """
    Extracts and validates IPv4 addresses from a raw string.

    Uses a hybrid approach: a Regular Expression to find potential IP formats
    and Python logic to ensure each octet is within the 0-255 range.

    Args:
        text (str): The raw string content to be analyzed.

    Returns:
        list[str]: A list of unique, valid IPv4 addresses found in the text.
    """
    found_ips = []
    pattern = r"\b(?:(?:0|[1-9]\d{0,2})\.){3}(?:0|[1-9]\d{0,2})\b"
    potential_ips = re.findall(pattern, text)

    for candidate in potential_ips:
        individual = candidate.split(".")
        is_valid = True
        for i in individual:
            if int(i) > 255:
                is_valid = False
                break
        if is_valid:
            found_ips.append(candidate)
    return list(set(found_ips))


def _extract_from_json(text) -> list[str]:
    try:
        data = json.loads(text)
        json_as_text = json.dumps(data)
        return _extract_from_regex(json_as_text)
    except json.JSONDecodeError:
        sys.exit("Error: Invalid JSON format.")


def get_ip_details(ip_list) -> list[dict]:
    """
    Fetches geolocation data from IP-API using Batch POST requests.

    Slices the input list into chunks of 50 to comply with API limits and
    implements a 1.5s delay between batches to respect rate-limiting.
    """
    all_results = []
    url = "http://ip-api.com/batch?fields=status,continent,regionName,city,org,query"
    for i in range(0, len(ip_list), MAX_BATCH_SIZE):
        batch = ip_list[i : i + MAX_BATCH_SIZE]
        content = [{"query": ip} for ip in batch]
        try:
            response = requests.post(url, json=content)
            response.raise_for_status()
            results = response.json()
            all_results.extend(results)
            if i + MAX_BATCH_SIZE < len(ip_list):
                time.sleep(1.5)
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")
    return all_results


def report(ip_details):
    """
    Formats and prints the final geographical report to the terminal.

    Filters successful API responses and generates a visual grid using 'tabulate'.
    Applies column width constraints to maintain readability.
    """
    table_data = []
    for item in ip_details:
        if item.get("status") == ("success"):
            table_data.append(
                [
                    item.get("query"),
                    item.get("city"),
                    item.get("regionName"),
                    item.get("continent"),
                    item.get("org"),
                ]
            )
    headers = ["IP ADDRESS", "CITY", "REGION", "CONTINENT", "ORGANIZATION"]
    widths = [None, None, None, None, 25]
    return tabulate(
        table_data, headers=headers, tablefmt="fancy_grid", maxcolwidths=widths
    )


def main() -> None:
    path = validate_input()
    valid_ip_list = ip_info(path)

    if not valid_ip_list:
        sys.exit("No valid IPs found in the provided file")

    print(f"Found {len(valid_ip_list)} unique IPs. Starting analysis...")

    ip_details = get_ip_details(valid_ip_list)

    output_table = report(ip_details)
    print(output_table)


if __name__ == "__main__":
    main()
