

from pathlib import Path


def get_words() -> set[str]:
    # return set(Path('/usr/share/dict/words').read_text().split('\n'))
    # https://www.kaggle.com/datasets/rtatman/english-word-frequency
    lines = Path('./unigram_freq.csv').read_text().split('\n')[1:]


CROSSWORD_LENGTH = 16
NUM_CHARS_FOR_LONG_WORD = CROSSWORD_LENGTH/2

def find_mustaches() -> list[tuple[str, str, str]]:
    words = get_words()
    words_with_8_chars = [w for w in words if len(w) == NUM_CHARS_FOR_LONG_WORD]
    print(f"{len(words_with_8_chars)=}")
    print(f"{words_with_8_chars[:5]=}")
    print(f"{words_with_8_chars[5:]=}")

    mustaches: list[tuple[str, str, str]] = []
    for word in words_with_8_chars:
        # split word into 2 words between 2 and 6 chars long
        for i in range(2, len(word)-1):
            w1, w2 = word[:i], word[i:]
            if w1 in words and w2 in words:
                print(word, w1, w2)
                mustaches.append((word, w1, w2))
    return mustaches

