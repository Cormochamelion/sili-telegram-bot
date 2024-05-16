import bs4
import os
import requests
import time


def get_dota_api_all_heroes() -> list[dict]:
    """
    Query the opendota webAPI for a description of all known heroes.
    """
    api_root = "https://api.opendota.com/api/"
    hero_path = "heroes"

    api_hero_endpoint = api_root + hero_path

    hero_response = requests.get(api_hero_endpoint)

    return hero_response.json()


def hero_names_from_heroes(heroes: list[dict]) -> list[str]:
    """
    Extract hero names from a list of hero entries as returned by the opendota webAPI.
    """
    return [hero_dict["localized_name"] for hero_dict in heroes]


def hero_name_to_wiki_url(hero_name: str) -> str:
    base_url = "https://liquipedia.net/dota2game/"
    hero_path = "_".join(hero_name.split(" "))

    return base_url + hero_path


def hero_name_to_mapicon_url(hero_name) -> str:
    hero_url = hero_name_to_wiki_url(hero_name)
    hero_response = requests.get(hero_url)
    hero_soup = bs4.BeautifulSoup(hero_response.content, features="html.parser")

    mapicon_selector = ".quote-source .pixelart"

    mapicon_tag = hero_soup.select(mapicon_selector)[0]
    mapicon_srcset = mapicon_tag["srcset"]
    mapicon_path = mapicon_srcset.split(" ")[0]

    return "https://liquipedia.net" + mapicon_path

def get_with_print(hero_name):
    print(f"Getting url for {hero_name}...")
    url = hero_name_to_mapicon_url(hero_name)
    print("... done, waiting before next...")
    time.sleep(15)
    print(f"... done with {hero_name}.")
    return(url)


def download_hero_png(url: str, hero_name: str) -> str:
    file_name = hero_name.replace(" ", "_") + ".png"

    file_path = os.path.join("resources", file_name)

    dl_response = requests.get(url)

    if not dl_response.status_code == 200:
        raise(f"Could not get a positive response from {url}")

    dl_file_handle = open(file_path, "wb")
    dl_file_handle.write(dl_response.content)

    return(file_path)


if __name__ == "__main__":
    hero_names = hero_names_from_heroes(get_dota_api_all_heroes())
    mapicon_urls = map(get_with_print, hero_names)
    mapicon_paths = map(
        lambda x: download_hero_png(x[0], x[1]), zip(mapicon_urls, iter(hero_names))
    )
    all_paths = [*mapicon_paths]