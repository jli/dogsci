#!/Users/j/src/dogsci/pldl/venv/bin/python3

#!/usr/bin/env python3

import requests
import sys
import m3u8
from pathlib import Path

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15'
}

def download_file(local_filename, playlist_url):
    if Path(local_filename).exists():
        raise ValueError(f'{local_filename} exists')
    base_url = playlist_url.rsplit('/', 1)[0] + '/'
    print(f'{base_url=}')

    r = requests.get(playlist_url, headers=headers)
    r.raise_for_status()
    m3u8_master = m3u8.loads(r.text)
    pl0 = m3u8_master.data['playlists'][0]
    pl0_copy = dict(pl0)
    pl0_copy.pop('uri')
    print(f"playlist: {pl0_copy}")

    r = requests.get(base_url + pl0['uri'], headers=headers)
    r.raise_for_status()
    m3u8_pl0 = m3u8.loads(r.text)

    with open(local_filename, 'wb') as f:
        segments = m3u8_pl0.data['segments']
        for i, segment in enumerate(segments, 1):
            print(f'{i}/{len(segments)} {i/len(segments):.1%} {local_filename}')
            if i > 1000:
                return
            url = base_url + segment['uri']
            req = requests.get(url, headers=headers)
            req.raise_for_status()
            f.write(req.content)


def main():
    fn = sys.argv[1]
    url = sys.argv[2]
    fn = fn.replace(': ', ' ').replace('&', 'and').strip()
    if not fn.endswith(".mp4"):
        fn += ".mp4"
    print(f'{fn=} {url=}')
    download_file(fn, url)



if __name__ == "__main__":
    main()
