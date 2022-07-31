import sys
import bisect
from typing import List, Optional, Tuple

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QCheckBox, QScrollArea, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QObject, pyqtSlot

from data import generate_data, SCORE_LABELS


class GameDev(QWidget):
    def __init__(self):
        super().__init__()

        # Data
        self.data = generate_data()
        self.unique_genres: List[str] = sorted(list(self.data))
        unique_games = set()
        for v in self.data.values():
            unique_games |= set(v)
        self.unique_games: List[str] = sorted(list(unique_games))

        # Init QT5
        self._init_app()

    def _init_app(self):
        def make_subtitle(title) -> QLabel:
            q_label = QLabel(title)
            q_label.setStyleSheet('font-size:20pt;'
                                  'font-weight:bold;')
            return q_label

        self.setWindowTitle('게임 개발 스토리 조합툴')
        self.main = QGridLayout()
        self.setMinimumWidth(700)
        self.setLayout(self.main)

        # Title
        self.main.addWidget(make_subtitle('장르'), 0, 0)
        self.main.addWidget(make_subtitle('게임'), 0, 1)
        self.main.addWidget(make_subtitle('결과'), 0, 2)

        # Selection Options
        genre_signal = SelectWidget.CheckBoxSignal()
        game_signal = SelectWidget.CheckBoxSignal()

        genre_signal.signal.connect(self.on_checkbox_changed)
        game_signal.signal.connect(self.on_checkbox_changed)
        self.genre_widget = SelectWidget(self.unique_genres, genre_signal)
        self.game_widget = SelectWidget(self.unique_games, game_signal)

        game_scroll = QScrollArea()
        game_scroll.setWidgetResizable(True)
        game_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        game_scroll.setWidget(self.game_widget)

        self.main.addWidget(self.genre_widget, 1, 0)
        self.main.addWidget(game_scroll, 1, 1)

        # Output
        self.output_widget = OutputWidget()
        output_scroll = QScrollArea()
        output_scroll.setWidgetResizable(True)
        output_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        output_scroll.setWidget(self.output_widget)
        self.main.addWidget(output_scroll, 1, 2)

        # Buttons
        reset_button = QPushButton('Reset')
        reset_button.pressed.connect(self.on_reset)
        self.main.addWidget(reset_button, 2, 2)

    @pyqtSlot()
    def on_checkbox_changed(self, ):
        genre_checks = self.genre_widget.list_checked()
        game_checks = self.game_widget.list_checked()

        checked_genres = [v for c, v in zip(genre_checks, self.unique_genres) if c]
        checked_games = [v for c, v in zip(game_checks, self.unique_games) if c]

        output_data = []
        for genre in checked_genres:
            for game in checked_games:
                if genre in self.data and game in self.data[genre]:
                    output_data.append((self.data[genre][game], genre, game))
        self.output_widget.set_data(output_data)

    @pyqtSlot()
    def on_reset(self):
        self.game_widget.clear_checkboxes()
        self.genre_widget.clear_checkboxes()


class SelectWidget(QWidget):
    class CheckBoxSignal(QObject):
        signal = pyqtSignal()

    def __init__(self, list_data: List[str], signal: CheckBoxSignal):
        super().__init__()
        self.list_data = list_data
        self.signal = signal
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setSpacing(0)
        self.setMinimumWidth(150)

        self.checkboxes: List[Optional[QCheckBox]] = [None] * len(self.list_data)
        for i, genre in enumerate(self.list_data):
            self.checkboxes[i] = QCheckBox(genre)
            self.checkboxes[i].stateChanged.connect(self.listen_checkbox_pressed)
            self.grid.addWidget(self.checkboxes[i], i, 0)

    def clear_checkboxes(self):
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setChecked(False)

    def listen_checkbox_pressed(self, state):
        self.signal.signal.emit()

    def list_checked(self) -> List[bool]:
        return [c.isChecked() for c in self.checkboxes]


class OutputWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.data = []
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.setAlignment(Qt.AlignTop)

    def set_data(self, output_data: List[Tuple[int, str, str]]):
        def make_labels(_score, _genre, _game) -> Tuple[QLabel, QLabel, QLabel]:
            _score_label = QLabel(SCORE_LABELS[_score])
            _score_label.setStyleSheet('font-weight:bold')
            _genre_label = QLabel(_genre)
            _game_label = QLabel(_game)
            return _score_label, _genre_label, _game_label

        # Clear
        self.data.clear()
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        # Sorted by Score
        self.data = sorted(output_data, key=lambda x: -x[0])

        # Add Items
        for i, (data_type, genre, game) in enumerate(self.data):
            score_label, genre_label, game_label = make_labels(data_type, genre, game)
            self.grid.addWidget(score_label, i, 0)
            self.grid.addWidget(genre_label, i, 1)
            self.grid.addWidget(game_label, i, 2)


def main():
    app = QApplication(sys.argv)
    game = GameDev()
    game.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
