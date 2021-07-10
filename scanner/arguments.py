from multiprocessing import cpu_count
import argparse

def parse_range(range_string):
    fields = range_string.split("-", 1)
    if len(fields) != 2 or not all(map(str.isdigit, fields)):
        raise argparse.ArgumentTypeError(
            f"'{range_string}' is not a valid ID range")

    fields = (int(fields[0]), int(fields[1]))
    if fields[0] > fields[1]:
        raise argparse.ArgumentTypeError(
            f"Start ID can't be larger than end ID")

    return fields

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--threads", type=int, default=50, help="Amount of threads to be created per worker")
    parser.add_argument("-w", "--workers", type=int, default=cpu_count(), help="Amount of processes to be created")
    parser.add_argument("-r", "--range", type=parse_range, help="Range of group ids to be scanned")
    parser.add_argument("-c", "--cut-off", type=int, help="Group ids past this point won't be blacklisted based on their current validity status.")
    parser.add_argument("-p", "--proxy-file", type=argparse.FileType("r", encoding="UTF-8", errors="ignore"), help="List of HTTP proxies")
    parser.add_argument("-u", "--webhook-url", type=str, help="Webhook for results")
    parser.add_argument("--chunk-size", type=int, default=100, help="Amount of groups to be checked per request")
    parser.add_argument("--timeout", type=float, default=5.0, help="Timeout for server responses")
    arguments = parser.parse_args()
    return arguments