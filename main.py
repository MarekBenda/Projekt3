"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Marek Benda
email: czechmarekbenda@gmail.com
"""

import requests
import csv
import sys
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple

# Base URL for fetching district URLs
BASE_URL = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"


def validate_arguments(args: List[str]) -> Tuple[str, str]:
    """
        Validate the command-line arguments.

        Args:
            args (List[str]): List of command-line arguments.

        Returns:
            Tuple[str, str]: Tuple of input value and CSV file name.

        Raises:
            SystemExit: If arguments are invalid.
    """
    if len(args) != 3:
        print("Chyba: Musíte zadat přesně dva argumenty: <URL nebo název okresu> <výstupní_soubor.csv>")
        sys.exit(1)

    input_value = args[1]
    csv_file = args[2]

    if not input_value:
        print("Chyba: První argument (URL nebo název okresu) nesmí být prázdný.")
        sys.exit(1)

    if "volby.cz" in input_value and not input_value.startswith("http"):
        print("Chyba: URL musí být úplná a začínat na 'http' nebo 'https'.")
        sys.exit(1)

    if not csv_file.lower().endswith('.csv'):
        print("Chyba: Druhý argument musí být název souboru s příponou '.csv'.")
        sys.exit(1)

    return input_value, csv_file


def validate_url(url: str) -> None:
    """
        Validate if a URL is reachable.

        Args:
            url (str): URL to validate.

        Raises:
            SystemExit: If URL is invalid or unreachable.
    """
    try:
        response = requests.head(url, timeout=5)
        if response.status_code != 200:
            print(f"Chyba: Zadaná URL není dostupná. Status code: {response.status_code}")
            sys.exit(1)
    except requests.RequestException:
        print("Chyba: Zadaná URL není platná nebo není dostupná.")
        sys.exit(1)


def fetch_page(url: str) -> BeautifulSoup:
    """
        Fetch and parse a webpage into a BeautifulSoup object.

        Args:
            url (str): URL of the page to fetch.

        Returns:
            BeautifulSoup: Parsed HTML content.

        Raises:
            SystemExit: If fetching fails.
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        sys.exit(1)
    return BeautifulSoup(response.text, 'html.parser')


def get_url_from_name(district_name: str) -> str:
    """
        Fetch the district URL based on its name.

        Args:
            district_name (str): Name of the district.

        Returns:
            str: URL of the district page.

        Raises:
            SystemExit: If district is not found.
    """
    if district_name.isdigit():
        print("Chyba: Název okresu nemůže být pouze číslo.")
        sys.exit(1)

    soup = fetch_page(BASE_URL)
    tables = soup.find_all('table', {'class': 'table'})

    for table in tables:
        rows = table.find_all('tr')[2:]  # Skip header rows
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 3:
                district_name_in_page = cells[1].text.strip()
                if district_name_in_page.lower() == district_name.lower():
                    url = cells[3].find('a')['href']
                    return f"https://www.volby.cz/pls/ps2017nss/{url}"

    print(f"District '{district_name}' not found.")
    sys.exit(1)


def extract_district_stats(soup: BeautifulSoup) -> Dict[str, str]:
    """
        Extract district-level statistics (registered, envelopes, valid votes).

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            Dict[str, str]: Dictionary with district statistics.
    """
    registered = soup.find('td', {'headers': 'sa2'})
    envelopes = soup.find('td', {'headers': 'sa3'})
    valid = soup.find('td', {'headers': 'sa6'})

    return {
        'registered': registered.text.strip().replace('\xa0', '') if registered else 'N/A',
        'envelopes': envelopes.text.strip().replace('\xa0', '') if envelopes else 'N/A',
        'valid': valid.text.strip().replace('\xa0', '') if valid else 'N/A',
    }


def extract_party_data(row: BeautifulSoup) -> Tuple[int, str, str] | None:
    """
        Extract party data (cislo, name, votes) from a table row.

        Args:
            row (BeautifulSoup): HTML row from the webpage.

        Returns:
            Tuple[int, str, str] | None: Tuple of (cislo, party_name, votes_count) or None if invalid.
    """
    cislo_cell = row.find('td', {'class': 'cislo', 'headers': ['t1sa1 t1sb1', 't2sa1 t2sb1']})
    party_name_cell = row.find('td', class_='overflow_name')
    vote_cells = row.find_all('td', class_='cislo')

    if cislo_cell and party_name_cell and len(vote_cells) > 1:
        try:
            cislo_value = int(cislo_cell.text.strip())
            party_name = party_name_cell.text.strip()
            votes_count = vote_cells[1].text.strip().replace('\xa0', '')
            return cislo_value, party_name, votes_count
        except ValueError:
            return None
    return None


def fetch_district_data(url: str) -> Tuple[Dict[str, str], List[Tuple[int, str]]]:
    """
        Fetch district data and party data, sorted by cislo.

        Args:
            url (str): URL of the district results page.

        Returns:
            Tuple[Dict[str, str], List[Tuple[int, str]]]: District data and sorted (cislo, party_name) list.
    """
    soup = fetch_page(url)
    district_data = extract_district_stats(soup)

    party_list = []
    for row in soup.find_all('tr'):
        party_data = extract_party_data(row)
        if party_data:
            party_list.append(party_data)

    party_list.sort(key=lambda x: x[0])

    for _, party_name, votes_count in party_list:
        district_data[party_name] = votes_count

    ordered_parties = [(cislo, party_name) for cislo, party_name, _ in party_list]
    return district_data, ordered_parties


def write_to_csv(csv_file: str, all_district_data: List[Dict[str, str]], ordered_party_names: List[str]) -> None:
    """
        Write election data to a CSV file.

        Args:
            csv_file (str): Output CSV file name.
            all_district_data (List[Dict[str, str]]): List of district data dictionaries.
            ordered_party_names (List[str]): List of party names in desired order.
    """
    csv_columns = ["code", "location", "registered", "envelopes", "valid"] + ordered_party_names

    try:
        with open(csv_file, mode="w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=csv_columns)
            writer.writeheader()
            for entry in all_district_data:
                row = {col: entry.get(col, "0") for col in csv_columns}
                writer.writerow(row)
        print(f"CSV soubor '{csv_file}' byl úspěšně vytvořen s UTF-8 zakódováním.")
    except Exception as e:
        print(f"Chyba při zápisu do CSV souboru: {str(e)}")
        sys.exit(1)


def process_district_row(row: BeautifulSoup) -> Tuple[str, str, str]:
    """
        Process a district row to extract code, name, and URL.

        Args:
            row (BeautifulSoup): HTML row from the district table.

        Returns:
            Tuple[str, str, str]: Tuple of (cislo_value, district_name, second_level_url).
    """
    cells = row.find_all('td')
    cislo_value = cells[0].find('a').text.strip()
    district_name = cells[1].text.strip()
    second_level_url = "https://www.volby.cz/pls/ps2017nss/" + cells[0].find('a')['href']
    return cislo_value, district_name, second_level_url


def main() -> None:
    """
        Main function to execute the election data extraction process.
    """
    input_value, csv_file = validate_arguments(sys.argv)

    if "volby.cz" in input_value:
        url = input_value
        validate_url(url)
    else:
        url = get_url_from_name(input_value)

    soup = fetch_page(url)
    rows = soup.find_all('tr')

    all_district_data = []
    all_ordered_parties = []

    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 1 and cells[0].get('class') == ['cislo']:
            cislo_value, district_name, second_level_url = process_district_row(row)
            district_data, ordered_parties = fetch_district_data(second_level_url)
            district_data['code'] = cislo_value
            district_data['location'] = district_name
            all_district_data.append(district_data)
            all_ordered_parties.extend(ordered_parties)

    if not all_district_data:
        print("Žádná data k exportu, ukončuji program.")
        sys.exit(1)

    all_ordered_parties.sort(key=lambda x: x[0])
    ordered_party_names = []
    seen = set()
    for _, party_name in all_ordered_parties:
        if party_name not in seen:
            ordered_party_names.append(party_name)
            seen.add(party_name)

    print("Zapisuji data do CSV souboru...")
    write_to_csv(csv_file, all_district_data, ordered_party_names)


if __name__ == "__main__":
    main()
