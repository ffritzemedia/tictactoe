import toga
from toga.style import Pack
from toga.colors import color, RED, BLACK, rgb
from toga.fonts import Font, SERIF
from .player import Ch_Player
from ..resources.state import GameHasEnded, State, StateException
from ..resources.qbot import QBot
from .statusdisplay import StatusDisplay


class Board ():
    def __init__(self):
        self._width=0
        self._height=0
        self._player : Ch_Player
        self._state : State
        self._qbot : QBot
        self.canvas = toga.Canvas(
            style=Pack(flex=1),
            on_resize=self._draw,
            on_press=self._on_press
            )
        self.context = self.canvas.context
        self.status_display : StatusDisplay
        
        
    def _draw(self, widget, width, height):
        ##Spielfeld zeichnen##
        self.context.clear()
        self._width=width
        self._height=height
        length = min(width, height)
        self.context.stroke_style = 'black'
        self.context.line_width = max(1,length/100)
        #Koordinaten für ein quadratisches zentriertes Spielfeld
        x1 = (width-length)/2 + length/3
        x2 = (width-length)/2 + 2 * length/3
        y1 = (height-length)/2 + length/3
        y2 = (height-length)/2 + 2*length/3
        #senkrechte Linien zeichnen
        self.context.begin_path()
        self.context.move_to(x1, (height-length)/2)
        self.context.line_to(x1, length/2+height/2)
        self.context.move_to(x2, (height-length)/2)
        self.context.line_to(x2, length/2+height/2)
        self.context.stroke()
        #wagerechte Linien zeichnen
        self.context.begin_path()
        self.context.move_to((width-length)/2, y1)
        self.context.line_to(length/2+width/2, y1)
        self.context.move_to((width-length)/2, y2)
        self.context.line_to(length/2+width/2, y2)
        self.context.stroke()
        #draw XO
        #self._drawXO(20,20,20,"X")
        for i in range (0,3):
            x = (width-length)/2 + i * length/3 + length/24
            if self._state._felder[i] == 1:
                self._drawXO(x,y1-length/24, length/4, "X")
            if self._state._felder[i] == -1:
                self._drawXO(x,y1-length/24, length/4, "O")
            if self._state._felder[i+3] == 1:
               self._drawXO(x,y2-length/24, length/4, "X")
            if self._state._felder[i+3] == -1:
               self._drawXO(x,y2-length/24, length/4, "O")
            if self._state._felder[i+6] == 1:
               self._drawXO(x,height/2 + length/2 -length/24, length/4, "X")
            if self._state._felder[i+6] == -1:
               self._drawXO(x,height/2 +length/2 -length/24, length/4, "O")
        if self._state._gameHasEnded:
            with self.canvas.Fill(color=rgb(255,120,0)) as text_filler:
                    font = toga.Font(family=SERIF, size=length/10)
                    # measure the actual text we will draw
                    text_width, text_height = self.canvas.measure_text("click to play", font)
                    # center horizontally; adjust vertically for baseline by adding half the text height
                    x = (width - text_width) / 2
                    y = height / 2 + text_height / 2
                    text_filler.write_text("click to play", x, y, font)
        
        
    def _drawXO(self,x,y,size,char):
        font = toga.Font(family=SERIF, size=size)
        self.text_width, text_height = self.canvas.measure_text(char, font)
        with self.canvas.Fill(color=rgb(0,103,71)) as text_filler:
            self.text = text_filler.write_text(char, x, y, font)
        
    
    def _on_press(self, widget, x, y):
        if self._state._gameHasEnded:
            self._state.reset()
            self.status_display.clear_status()
            # notify player UI to reflect reset/next player
            if hasattr(self, '_player') and self._player:
                try:
                    self._player.update()
                except Exception:
                    pass
            if self._state._nextPlayer == -1: #QBot ist dran
                self._qbot.make_move()
                if hasattr(self, '_player') and self._player:
                    try:
                        self._player.update()
                    except Exception:
                        pass
            self._draw(widget, self._width,self._height)
            self.setLabels()
            return
        #print(f"({x},{y})")
        feld = -1
        length = min(self._height, self._width)
        # placwment calculation
        offX = (self._width-length)/2
        offY = (self._height-length)/2
        if x<offX or y<offY:
            pass
        elif x < offX + length/3:
            if y < offY+length/3:
                feld = 0 #print("Feld 0")
            elif y < offY + 2 * length/3:
                feld = 3 #print("Feld 3")
            elif y < offY + length:
                feld = 6 #print("Feld 6")
        elif x < offX + 2 * length/3:
            if y < offY + length/3:
                feld = 1 #print("Feld 1")
            elif y < offY + 2 * length/3:
                feld = 4 #print("Feld 4")
            elif y < offY + length:
                feld = 7 #print("Feld 7")
        elif x < offX + length:
            if y < offY + length/3:
                feld = 2 #print("Feld 2")
            elif y < offY + 2 * length/3:
                feld = 5 #print("Feld 5")
            elif y < offY + length:
                feld = 8 #print("Feld 8")
        if feld != -1:
            try:
                if self._state._nextPlayer == 1: # Mensch ist dran
                    result = self._state.setNext(feld)
                    #QBot lernt aus dem Ergebnis, falls das Spiel zu Ende ist
                    if result is not None:
                        self._qbot.learn(result)
                        self.status_display.game_has_ended(result)
                    '''
                    if result == -1:
                        self._qbot.learn(3)
                    elif result == 1:
                        self._qbot.learn(-1)
                    elif result == 0:
                        self._qbot.learn(1)
                        '''
                    self._draw(widget, self._width,self._height)
                    self.setLabels()
                if self._state._nextPlayer == -1:
                    result = self._qbot.make_move()
                    if result is not None:
                        self._qbot.learn(result)
                        self.status_display.game_has_ended(result)
                self._draw(widget, self._width,self._height)
                self.setLabels()
                #print ("\n",self._state._felder[0:3], "\n",self._state._felder[3:6], "\n", self._state._felder[6:])
            except StateException as e:
                #print(e.message)
                self.status_display.update_status(e.message)
            except GameHasEnded as e:
                self.status_display.update_status(e.message)
                #print(e)
        else:
            raise BaseException("Bitte ins Feld klicken.")
        
    def setLabels(self):
        self._player.button.text = "O" if self._state._nextPlayer == -1 else "X"
        self._player.label.text = "Wähle Startspieler" if self._state._gameHasEnded else "Nächster Spieler"
        if self._state._gameHasEnded:
            self._player.button.enabled = True
        else:
            self._player.button.enabled = False
        
class BoardException(Exception):
    def __init__(self, message):
        super().__init__(self)
        self.message = message