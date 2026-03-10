#from ..gui.board import Board

class State():
    def __init__(self, felder = [0 for i in range(0,9)], nextPlayer = 1, gameHasEnded = True):
        '''
        Initialisierung des Spielzustands mit Feldern, nächstem Spieler und Spielende-Flag.

        :param self: State-Instanz
        :param felder: Liste der Felder im Spiel (0 für leer, 1 für X, -1 für O), links oben beginnend zeilenweise
        :param nextPlayer: Beschreibt den nächsten Spieler (1 für X oder -1 für O)
        :param gameHasEndet: Flag ob das Spiel beendet ist
        :type felder: list[int]
        '''
        #self._board : Board = None
        self._felder = felder
        self._nextPlayer = nextPlayer
        self._startPlayer = nextPlayer
        self._gameHasEnded = gameHasEnded
        self.open_matchboxes = [] # History of moves during the game for learning later.
        # Testzustand
        self._felder[0] = 1
        self._felder[4] = -1
        
    
    def setNext(self, feld : int):
        '''
        Setzt das nächste Feld im Spiel je nach dem aktuellen Spieler.
        
        :param self: State-Instanz
        :param feld: Beschreibt das zu besetzende Feld (0-8)
        :type feld: int
        '''
        if self._gameHasEnded:
            raise GameHasEnded()
        if self._felder[feld] == 0:
            #print(f"write to history: {self.state_to_string() + str(feld)}")
            self.open_matchboxes.append(self.state_to_string() + str(feld)) # Store the state before making the move for learning later.
            self._felder[feld] = self._nextPlayer # mark the field for the current player
            self._nextPlayer *= -1
            win = self.playerWinns()
            if win is not None:
                print (f"Player {win} hat gewonnen")
            return win
        else:
            raise StateException(f"Feld {feld} ist bereits belegt, Zug nicht möglich")
        
    def state_to_string(self):
        '''
        Converts the current game state to a string representation.
        Toggls the field values by the next player
        Shifts the field values by 1 to avoid negative values to get a uniform length of 9 for the field plus 1 for the next player.

        :param self: The State instance.
        '''
        felder = ''.join([str(x * self._nextPlayer + 1) for x in self._felder])
        player = str(self._nextPlayer + 1)
        return felder + player
    
    def playerWinns(self):
        '''
        Prüft, ob ein Spieler gewonnen hat.

        :param self: State-Instanz
        '''
        values = list()
        #Spaltensummen
        for i in range(0,3):
            values.append(sum(self._felder[i::3]))
        #Zeilensummen
        for i in range(0,8,3):
            values.append(sum(self._felder[i:i+3]))
        #Summen der Diagonalen
        values.append(sum(self._felder[0::4]))
        values.append(sum(self._felder[2:7:2]))
        #Prüfung ob und wer gewonnen
        if max(values) == 3:
            self._gameHasEnded = True
            self._nextPlayer = self._startPlayer
            return 1
        elif min(values) == -3:
            self._gameHasEnded = True
            self._nextPlayer = self._startPlayer
            return -1
        elif not self._felder.__contains__(0):
            self._gameHasEnded = True
            self._nextPlayer = self._startPlayer
            return 0
        else:
            return None
        
    def reset(self):
        '''
        Setzt den Spielzustand zurück auf die ursprünglichen Defaukt-Werte.

        :param self: State-Instanz
        '''
        self._felder = [0 for i in range(0,9)]
        self._nextPlayer = self._startPlayer
        self._gameHasEnded = False
        
        

class StateException(Exception):
    def __init__(self, message, *args):
        super().__init__(*args)
        self.message = message

class GameHasEnded(Exception):
    def __init__(self, *args):
        super().__init__(*args)
