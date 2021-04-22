import argparse
import random

from typing import List, Optional


def read_words(path: str, charlow: Optional[int], charhigh: Optional[int]) -> List[str]:
    "Return normalized list of words from path."
    def lencheck(s: str) -> bool:
        l = len(s)
        if charlow and l < charlow:
            return False
        if charhigh and l > charhigh:
            return False
        return True

    with open(path) as f:
        words = [word.strip().lower() for word in f if lencheck(word)]
        if not words:
            raise RuntimeError(f"failed to load words from {path} with length bounds [{charlow}, {charhigh}]")
        return words


def generate_phrase(words: List[str], sep: str, num_words: int, mixcase: bool) -> str:
    def caseshift(w: str) -> str:
        return w.upper() if mixcase and random.randint(0, 1) else w

    chosen = (caseshift(w) for w in random.choices(words, k=num_words))
    return sep.join(chosen)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-words", default="/usr/share/dict/words")
    p.add_argument("-sep", default="-")
    p.add_argument("-num_words", type=int, default=4)
    p.add_argument("-no-mixcase", dest="mixcase", action="store_false")
    p.add_argument("-charlim", type=int, nargs="+",
                   help="per-word character limits")
    p.set_defaults(mixcase=True)
    args = p.parse_args()

    charlow = None
    charhigh = None
    if args.charlim is None:
        charlow = 3
        charhigh = 9
    else:
        if len(args.charlim) == 1:
            charhigh = args.charlim[0]
        elif len(args.charlim) == 2:
            charlow = args.charlim[0]
            charhigh = args.charlim[1]
        else:
            p.error("-charlim takes 1 or 2 arguments only")

    words = read_words(args.words, charlow, charhigh)
    phrase = generate_phrase(words, args.sep, args.num_words, args.mixcase)
    print(phrase)


if __name__ == "__main__":
    main()
