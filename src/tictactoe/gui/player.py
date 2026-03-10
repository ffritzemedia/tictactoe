import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from ..resources.state import State

class Ch_Player():
    def __init__(self, state: State):
        self._state = state
        self.player = self.setBox()
    
    
    def ch_player(self, widget):
        if self._state._gameHasEnded:
            self._state._startPlayer *= -1
            self._state._nextPlayer = self._state._startPlayer
            self.button.text = "O" if self._state._nextPlayer == -1 else "X"
            
    def setBox(self):
        # fixed width so the box always keeps the same size
        BOX_WIDTH = 160
        box = toga.Box(style=Pack(direction=COLUMN, padding=5, alignment='center', justify_content='center', align_items='center', width=BOX_WIDTH))
        label_text = lambda: "Wähle Startspieler" if self._state._gameHasEnded else "Nächster Spieler"
        self.label = toga.Label(label_text(), style=Pack(padding_bottom=5, font_size=14, alignment='center'))
        box.add(self.label)
        button_text = lambda: "O" if self._state._nextPlayer == -1 else "X"
        # make button fill most of the fixed box width (leave padding)
        self.button = toga.Button(button_text(), on_press=self.ch_player, style=Pack(flex=0, padding=5, width=BOX_WIDTH-20, height=80, font_size=36))
        box.add(self.button)
        return box