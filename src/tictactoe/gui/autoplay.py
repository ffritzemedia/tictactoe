import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from .board import Board
from ..resources.qbot import QBot

class AutoPlay():
    def __init__(self, qbot: QBot, board: Board):
        self._qbot = qbot
        self._board = board
        self._rounds = 10
        self.autoplay_box = self.setBox()
    
    def autoplay(self, widget=None):
        try:
            rounds = int(self.input.value)
        except ValueError:
            try:
                rounds = int(self.input.placeholder)
            except ValueError:
                rounds = 10
        for _ in range(rounds):
            self._board._state._gameHasEnded = False
            while not self._board._state._gameHasEnded:
                self._qbot.make_move()
                self._board._draw(self._board.canvas, self._board._width, self._board._height)
                self._board.setLabels()
            self._board._state.reset()
        self._board._state._gameHasEnded = True
        self._board._draw(self._board.canvas, self._board._width, self._board._height)
        self._board.setLabels()

    def setBox(self):
        # fixed width so the box always keeps the same size
        BOX_WIDTH = 160
        box = toga.Box(style=Pack(direction=COLUMN, padding=5, alignment='center', justify_content='center', align_items='center', width=BOX_WIDTH))
        label = toga.Label("Runden Autoplay:", style=Pack(padding_bottom=5, font_size=14, alignment='center'))
        self.input = toga.TextInput(style=Pack(padding_bottom=5, font_size=14, alignment='center'), placeholder="10")
        # pass the callable, do NOT call autoplay here (no parentheses)
        self.button = toga.Button("OK", on_press=self.autoplay, style=Pack(flex=0, padding=5, width=BOX_WIDTH-20, height=80, font_size=24))
        box.add(label)
        box.add(self.input)
        box.add(self.button)
        return box