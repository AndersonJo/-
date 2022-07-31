import csv
from pathlib import Path
from typing import Dict

FILE_SCORES = [
    ('raw/best.csv', 4),
    ('raw/unique.csv', 2),
    ('raw/not_bad.csv', 1),
]

TRANSLATIONS = {
    '어드벤쳐': '어드벤처'
}

SCORE_LABELS = {
    4: '걸작',
    2: '독창적',
    1: '나쁘지 않음'
}


def generate_data() -> Dict[str, Dict[str, int]]:
    def preprocess_games(word, score) -> dict:
        word = list(word)
        start = None
        for i, c in enumerate(word):
            if c == '[':
                start = i
            elif c == ']':
                word[start:i + 1] = ['']
        word = ''.join(word)
        return {game.strip(): score for game in word.split(',')}

    data = dict()
    for file_path, score in FILE_SCORES:
        file_path = Path(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for col in reader:
                genre = col[0]
                genre = genre.replace('게임', '').strip()
                genre = TRANSLATIONS.get(genre, genre)
                data.setdefault(genre, dict())

                games = preprocess_games(col[1], score)
                data[genre].update(games)
    return data


if __name__ == '__main__':
    generate_data()
