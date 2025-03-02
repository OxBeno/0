#!/usr/bin/env python3

import requests
import argparse
from concurrent.futures import ThreadPoolExecutor

def ensure_scheme(domain):
    if not domain.startswith(('http://', 'https://')):
        domain = f"https://{domain}"
    return domain

def send_request(domain):
    try:
        domain = ensure_scheme(domain)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(domain, headers=headers, timeout=5)
        return domain, response.status_code
    except requests.exceptions.RequestException as e:
        return domain, str(e)

def send_requests(domains):
    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_domain = {executor.submit(send_request, domain): domain for domain in domains}
        for future in future_to_domain:
            domain, status = future.result()
            results[domain] = status
            print(f"Domain: {domain} | Status: {status}")
    return results

def read_domains_from_file(file_path):
    with open(file_path, 'r') as file:
        domains = [line.strip() for line in file if line.strip()]
    return domains

def main():
    parser = argparse.ArgumentParser(description="Send HTTP requests to multiple domains and retrieve status codes.")
    parser.add_argument("-f", "--file", required=True, help="Path to the file containing domains (one per line).")
    parser.add_argument("-o", "--output", help="Path to the output file to save results.")
    args = parser.parse_args()

    domains = read_domains_from_file(args.file)
    results = send_requests(domains)

    if args.output:
        with open(args.output, "w") as output_file:
            for domain, status in results.items():
                output_file.write(f"{domain}: {status}\n")
        print(f"Results saved to {args.output}")

if __name__ == "__main__":
    main()
