#!/usr/bin/env python

import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable, Iterator, NamedTuple

import bs4
import requests
from rich.progress import track


logging.basicConfig(level=logging.INFO)


class ComicRef(NamedTuple):
    index: int
    url: str
    hovertext: str

    def filename(self) -> Path:
        text = self.hovertext.replace(" ", "_")
        text = re.sub("[^a-zA-Z0-9_]", "", text)
        return Path(f"{self.index:04}_{text}.png")

    def download_image(self) -> None:
        comic_soup = fetch_soup(self.url)
        image_url = comic_soup_to_image_url(comic_soup)
        image_bytes = requests.get(image_url).content
        self.filename().write_bytes(image_bytes)

    def to_dict(self) -> dict[str, Any]:
        d = self._asdict()
        d["filename"] = str(self.filename())
        return d


def fetch_soup(url: str) -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(requests.get(url).content, features="html.parser")


def get_all_comic_refs() -> list[ComicRef]:
    archive_soup = fetch_soup("https://asofterworld.com/archive.php")
    comic_anchors = [
        a
        for a in archive_soup.find_all("a")
        if a.attrs["href"].startswith("http://www.asofterworld.com/index.php?id=")
    ]
    # drop id=0 fnord
    logging.info(
        f"dropping first comic anchor to id=0 which isn't a real comic: {comic_anchors[0]}"
    )
    real_comic_anchors = comic_anchors[1:]
    return [parse_comic_anchor(a) for a in real_comic_anchors]


def parse_comic_anchor(a: bs4.element.Tag) -> ComicRef:
    index = int(
        a.attrs["href"].removeprefix("http://www.asofterworld.com/index.php?id=")
    )
    return ComicRef(index=index, url=a.attrs["href"], hovertext=a.text)


def comic_soup_to_image_url(comic_soup: bs4.BeautifulSoup) -> str:
    return comic_soup.select("div#comicimg img")[0].attrs["src"]


def write_metadata_json(comic_refs: Iterable[ComicRef]) -> None:
    with Path("metadata.ndjson").open("w") as f:
        for ref in comic_refs:
            f.write(json.dumps(ref.to_dict()) + "\n")


def download_all_comics() -> None:
    comic_refs = get_all_comic_refs()
    logging.info(f"parsed {len(comic_refs)} comics. downloading...")
    with ThreadPoolExecutor() as e:
        futs = {}
        for ref in comic_refs:
            futs[e.submit(ref.download_image)] = ref
        for fut in track(as_completed(futs), total=len(comic_refs)):
            # logging.info(f"finished fetching {futs[fut]}")
            pass
    logging.info("finished downloading all comics")
    write_metadata_json(comic_refs)


if __name__ == "__main__":
    download_all_comics()
