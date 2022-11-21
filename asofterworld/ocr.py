#!/usr/bin/env python

# todo:
# - doesn't work that well... try upscaling first?
# - threadpool didn't help. try process pool instead

from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import logging
from pathlib import Path
from typing import Iterable

from PIL import Image
from PIL import ImageFile
import pytesseract
from rich.progress import track

logging.basicConfig(level=logging.INFO)


COMICS_SUBDIR = "comics_superres2x"

def read_metadata_json() -> list[dict]:
    return [
        json.loads(line) for line in Path("metadata.ndjson").read_text().splitlines()
    ]


def chop_comic_frames(image: Image.Image) -> Iterable[Image.Image]:
    if image.height not in (261, 275, 525, 550, 1100) or image.width not in (720, 1440, 2880):
        logging.info(f"weird image dimensions: {image.width}, {image.height}")
    # using ratio so this works for upscaled images
    approx_row_height = image.width / 2.62
    num_rows = round(image.height / approx_row_height)
    for row_num in range(num_rows):
        last_row = row_num + 1 == num_rows
        for col_num in range(3):
            start_x = round(image.width * col_num / 3)
            end_x = round(image.width * (col_num + 1) / 3)
            start_y = round(image.height * row_num / num_rows)
            end_y = round(image.height * (row_num + 1) / num_rows)
            if last_row:
                # trim the artist name and web page
                end_y -= 20 * (1 if image.width < 2000 else 4)
            yield image.crop((start_x, start_y, end_x, end_y))


def do_ocr(filename: str) -> list[str]:
    image = Image.open(filename)
    return [
        pytesseract.image_to_string(frame).replace("\n", "  ").strip()
        for frame in chop_comic_frames(image)
    ]


def augment_metadata_with_ocr(d: dict) -> dict:
    """augment original metadata json dict with OCR"""
    frame_texts = do_ocr(f"{COMICS_SUBDIR}/" + d["filename"])
    return {**d, "ocr": frame_texts}


def write_ocr_metadata_json(metadata_with_ocr: Iterable[dict]) -> None:
    metadata_with_ocr = sorted(metadata_with_ocr, key=lambda d: d["index"])
    with Path("metadata_ocr__wut.ndjson").open("w") as f:
        for d in metadata_with_ocr:
            f.write(json.dumps(d) + "\n")


def do_all_ocr() -> None:
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    comics_metadata = read_metadata_json()
    results = []
    with ProcessPoolExecutor() as e:
        futs = []
        for metadata in comics_metadata:
            futs.append(e.submit(augment_metadata_with_ocr, metadata))
        for i, fut in track(enumerate(as_completed(futs), 1), total=len(comics_metadata)):
            metadata_with_ocr = fut.result()
            print(f"{i}/{len(comics_metadata)} parsed: {metadata_with_ocr['ocr']}")
            results.append(metadata_with_ocr)
    # for i, metadata in enumerate(comics_metadata, 1):
    #     metadata_with_ocr = augment_metadata_with_ocr(metadata)
    #     print(f"{i}/{len(comics_metadata)} parsed: {metadata_with_ocr['ocr']}")
    #     results.append(metadata_with_ocr)
    write_ocr_metadata_json(results)
    logging.info("all done")


if __name__ == "__main__":
    do_all_ocr()
