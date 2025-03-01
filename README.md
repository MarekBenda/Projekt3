# Czech Election Data Scraper
This Python script extracts election data from the 2017 Czech parliamentary election results available on https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ&xkraj=2&xdistr=0. It fetches town-level statistics (e.g., registered voters, envelopes issued, valid votes) and party vote counts based on the inputed districts, then saves the data into a CSV file. The script can process either a specific URL or a district name provided as a command-line argument.


## Features
* Validates command-line arguments (URL or district name, output CSV file).
* Scrapes district-to-town-level election statistics and party vote counts.
* Supports UTF-8 encoding for CSV output.
* Sorts party data consistently across districts.

## Prerequisites
To run this script, you need the following:
Software
* Python 3.6+: The script uses type hints and requires a modern Python version.
* pip: Python package manager to install dependencies.
* Internet Access: Required to fetch data from volby.cz.

## Installation
Clone or download this repository/script to your local machine.

Install the required Python libraries:

Either using a requirements.txt file provided:
```bash
pip install -r requirements.txt
```

or using:
```bash
pip install requests beautifulsoup4
```


## Usage
Run the script from the command line with two arguments:
* Input: Either a URL to a specific district (like Praha-východ after you click on the "X" for "Výběr obce") election results page or the name of a district (e.g., "Praha").
* Output: The name of the CSV file to save the results (must end with .csv).

Syntax
```bash
python script.py <URL_or_district_name> <output_file.csv>
```

## Examples
Using a district name:
```bash
python script.py "Praha" praha_results.csv
```
Fetches election data for Prague and saves it to praha_results.csv.

Using a specific URL:
```bash
python script.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=1&xnumnuts=1100" praha_results.csv
```
Fetches data from the provided URL and saves it to praha_results.csv.

A shortened sample output for either:
```csv
code	location	registered	envelopes	valid	Občanská demokratická strana	Řád národa - Vlastenecká unie	CESTA ODPOVĚDNÉ SPOLEČNOSTI
500054	Praha 1	21556	14167	14036	2770	9	13
```

### Notes
* If using a URL, it must be a full URL starting with http or https and pointing to a valid volby.cz election results page.
* District names must match those listed on the base URL (https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ).
* The output CSV file will be overwritten if it already exists.

## Output
The script generates a CSV file with the following columns:
* ```code```: District code.
* ```location```: Town name name.
* ```registered```: Number of registered voters.
* ```envelopes```: Number of issued envelopes.
* ```valid```: Number of valid votes.
* Additional columns for each political party, with their respective vote counts.

The CSV uses UTF-8 encoding to work correctly with Czech accents.


## Error Handling
The script includes validation and error handling for:
* Invalid or missing command-line arguments.
* Unreachable or invalid URLs.
* Missing districts or data.
* File writing errors.

Error messages are printed in Czech (e.g., "Chyba: Zadaná URL není dostupná.") to match the target website’s language.

# Functions
Below is a brief overview of the key functions used in the script and their purposes:

* ```validate_arguments(args)```: Checks if the command-line arguments (input value and CSV file name) are valid and properly formatted.
* ```validate_url(url)```: Verifies that a provided URL is reachable by sending a HEAD request.
* ```fetch_page(url)```: Downloads a webpage and converts it into a BeautifulSoup object for HTML parsing.
* ```get_url_from_name(district_name)```: Looks up the URL of a district by its name from the base election page.
* ```extract_district_stats(soup)```: Pulls district-level stats (registered voters, envelopes, valid votes) from parsed HTML.
* ```extract_party_data(row)```: Extracts party details (number, name, vote count) from a single HTML table row.
* ```fetch_district_data(url)```: Combines district stats and sorted party data from a district’s results page.
* ```write_to_csv(csv_file, all_district_data, ordered_party_names)```: Saves all collected data into a structured CSV file.
* ```process_district_row(row)```: Processes a district row to get its code, name, and URL for further scraping.
* ```main()```: Coordinates the entire scraping and data export process.

## Limitations
* Designed specifically for the 2017 Czech parliamentary election results structure from volby.cz (as of 2025-01-03).
* Assumes the webpage structure remains consistent with the 2017 format.

## License
This project is open-source and available under the MIT License (LICENSE). Feel free to modify and distribute it as needed.

## Acknowledgments
Built with Python, requests, and BeautifulSoup.

Data sourced from the official Czech election website: volby.cz.

