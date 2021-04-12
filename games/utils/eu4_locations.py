"""Scrape eu4 locations so we can include them in voice commands.

Scraping requires a few dependencies. Don't worry about these unless you're
re-scraping the data. You shouldn't need to scrape the locations once the list
exists on disk.

This file isn't really meant to be run in Talon. Spin up a python instance with
the dependencies and scrape with that. You only need to do it once.

"""


import itertools
import os
import json


class URLS:
    # These pages are dedicated to tables.
    GEOGRAPHIC_PROVINCES = "https://eu4.paradoxwikis.com/Geographical_list_of_provinces"
    ECONOMIC_PROVINCES = "https://eu4.paradoxwikis.com/Economic_list_of_provinces"
    POLITICAL_PROVINCES = "https://eu4.paradoxwikis.com/Political_list_of_provinces"
    # We use a different wiki for the country list because it's easier to
    # navigate with BeautifulSoup.
    COUNTRIES = "https://europauniversalis.fandom.com/wiki/Country_ID"


def _root(url):
    """Get root BeautifulSoup element from ``url``."""
    import requests
    from bs4 import BeautifulSoup

    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")


def _extract_tables(element):
    """Extract all tables from a BeautifulSoup element."""
    tables = element.find_all("table")
    if tables:
        return tables
    else:
        raise RuntimeError("Could not find tables.")


def _extract_text(cell):
    return cell.text.strip() if cell.text else ""


def _to_text(row):
    """Extract a list of text items from a list of cells."""
    return [_extract_text(td) for td in row.select("td")]


def _table_to_df(table):
    """Convert a BeautifulSoup Table to a pandas DataFrame."""
    import pandas as pd

    # Can't search for "thead" for some reason.
    headers = [_extract_text(th) for th in table.findAll("th")]
    # TODO: What should this comment be?
    # First two columns in pandas are indicators.
    # headers[:2] = ["", " "]
    # print("All rows: ", table.findAll("tr"))
    body = [_to_text(row) for row in table.findAll("tr")]
    df = pd.DataFrame(body, columns=headers)
    # Top row might be all None - if so remove it.
    return df.dropna(how="all").reset_index(drop=True)


def tables_from_page(url):
    """Get all tables from an eu4wiki page, as a pandas dataframe."""
    return list(map(_table_to_df, _extract_tables(_root(url))))


def _normalize_element(element):
    """Normalize ``element`` for the speech engine."""
    from unidecode import unidecode

    if isinstance(element, str):
        # We want it lowercase, without accents.
        return unidecode(element).lower()
    else:
        return None


def _speech_normalize(data_frame):
    """Normalize all elements of ``data_frame`` for a speech engine.

    This removes accents, and makes everything lowercase.

    """
    return data_frame.applymap(_normalize_element)


def scrape_provinces():
    """Scrape all info about all provinces.

    :returns DataFrame: with each province plus as much information about it as
      is available.

    """
    PROVINCE_KEY = "Name"
    # We assume the only table on each of these pages is the table we want.
    # Might change, so this could be fragile.
    geographic = tables_from_page(URLS.GEOGRAPHIC_PROVINCES)[0]
    economic = tables_from_page(URLS.ECONOMIC_PROVINCES)[0]
    political = tables_from_page(URLS.POLITICAL_PROVINCES)[0]
    assert PROVINCE_KEY in geographic, geographic
    assert PROVINCE_KEY in economic, economic
    assert PROVINCE_KEY in political
    merged = geographic.merge(
        economic.merge(political, on=PROVINCE_KEY), on=PROVINCE_KEY
    )
    # Make it clearer what the "name" column is.
    merged = merged.rename(columns={"Name": "Province"})
    return _speech_normalize(merged)


def scrape_countries():
    """Scrape a list of all countries."""
    import pandas as pd

    # The countries are split into one table per alphabet letter - pull them
    # all & merge them
    countries = pd.concat(tables_from_page(URLS.COUNTRIES))
    assert "Country" in countries, countries
    return _speech_normalize(countries)


LOCATIONS_PATH = os.path.join(os.path.dirname(__file__), "eu4_locations.json")


def scrape_to_file():
    """Scrape all findable EU4 locations to a file."""
    print("Scraping locations...")
    # TODO: Maybe ensure they have the right form?
    location_lists = extract_lists(scrape_countries(), scrape_provinces())
    locations = itertools.chain(*location_lists.values())
    locations = list(filter(lambda item: isinstance(item, str), locations))
    with open(LOCATIONS_PATH, "w") as f:
        json.dump(locations, f)
    print(f"Done scraping. Scraped {len(locations)} locations.")


def extract_lists(countries_df, provinces_df):
    """Extract standardized lists from the scraped data frames."""
    # TODO: Clean up the method, it's overcomplicated now. We can only jump to
    #   countries & provinces.
    unprocessed = {
        "countries": countries_df["Country"],
        "provinces": provinces_df["Province"],
    }
    return {key: set(df.dropna()) for key, df in unprocessed.items()}


def load_locations():
    """Load locations that can be searched with the find tool."""
    if not os.path.isfile(LOCATIONS_PATH):
        raise RuntimeError(
            f"EU4 locations not scraped. Please run `python {__file__}` to scrape valid locations "
            "from the net. It has dependencies so run it with a dedicated interpreter, not Talon."
        )
    with open(LOCATIONS_PATH, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    print("Re-scraping dependencies...")
    scrape_to_file()
