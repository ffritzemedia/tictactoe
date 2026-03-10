from .table import SQLTable, Local_DB
from .state import State, StateException, GameHasEnded
import random

class QBot:
    def __init__(self, db, state : State):
        self._db = db
        self._state = state
        
    def state_to_string(self):
        '''
        Converts the current game state to a string representation.
        Shifts the field values by 1 to avoid negative values to get a uniform length of 9 for the field plus 1 for the next player.

        :param self: The QBot instance.
        '''
        felder = ''.join([str(x * self._state._nextPlayer + 1) for x in self._state._felder])
        return felder
    
    def create_moves_string(self):
        """
        Creates a string of available moves.

        :param self: The QBot instance.
        """
        moves = [str(i) for i in range(9) if self._state._felder[i] == 0]
        return ''.join(moves)
    
    def make_move(self):
        '''
        Makes a random move based on the Q-learning database and updates the open matchboxes by the current state and chosen move.

        :param self: The QBot instance.
        '''
        state_str = self.state_to_string()
        if self._db.has_state(state_str):
            moves_str = self._db.get_moves(state_str)
            if moves_str == '' or moves_str is None: # no available moves, recreate moves string
                moves_str = self.create_moves_string()
                self._db.update_moves(state_str, moves_str)
            import random
            move = int(random.choice(moves_str))
            try:
                return self._state.setNext(move) # male the move and check if the game has ended
            except StateException as e:
                print(f"QBot attempted invalid move: {e.message}")
        else: # no matchbox for this state, create one with all available moves and try again
            moves_str = self.create_moves_string()
            self._db.set_state(state_str, moves_str)
            return self.make_move()
            
    def learn(self, result: int):
        '''
        Updates the Q-learning database based on the game outcome.
        All opened matchboxes during the game are updated with the given reward. Rewards should be -1 for a loss, +1 for a draw, and +3 for a win.

        :param self: The QBot instance.
        :param reward: The reward value.
        :type reward: int
        '''
        while self._state.open_matchboxes != []:
            MAX_LEN = 18
            matchbox = self._state.open_matchboxes.pop()
            if not self._db.has_state(matchbox[0:9]): 
                # Create the matchbox if it does not exist, might happen for human player
                moves_str = self.create_moves_string()
                self._db.set_state(matchbox[0:9], moves_str)
            moves_str = str(self._db.get_moves(matchbox[0:9])) # first 9 characters represent the state, loads the moves for that state out of the database
            print(f"Updating matchbox {matchbox} with result {result}. Current moves: {moves_str}")
            # Update moves based on the result for player -1 (QBot)
            if matchbox[9] == '0': # QBot made the move
                print('updating for QBot')
                if result < 1:  # win or draw
                    moves_str += (-2 * result + 1) * matchbox[10]  # add move char based on result win (result = -1) or draw (result =0)
                    while len(moves_str) > MAX_LEN:
                        # remove a random character to shrink moves_str to MAX_LEN
                        idx = random.randrange(len(moves_str))
                        moves_str = moves_str[:idx] + moves_str[idx+1:]
                    self._db.update_moves(matchbox[0:9], moves_str)
                elif result == 1 and matchbox[10] in moves_str:
                    moves_str = moves_str.replace(matchbox[10], '', 1)
                    if moves_str == '' or moves_str is None:
                        # reconstruct available moves from the stored state (first 9 chars)
                        moves = [str(i) for i in range(9) if int(matchbox[i])-1 == 0] # -1 to revert to original field values
                        moves_str = ''.join(moves)
                        print(f"Replenishing moves for matchbox {matchbox[0:10]} to {moves_str}")
                    self._db.update_moves(matchbox[0:9], moves_str)   
            # update moves based on the result for player 1 (human)
            else: # human made the move
                print('updating for human')
                if result > -1:  # win or draw
                    moves_str += (2 * result + 1) * matchbox[10]
                    while len(moves_str) > MAX_LEN:
                        # remove a random character to shrink moves_str to MAX_LEN
                        idx = random.randrange(len(moves_str))
                        moves_str = moves_str[:idx] + moves_str[idx+1:]
                    self._db.update_moves(matchbox[0:9], moves_str)
                elif result == -1 and matchbox[10] in moves_str:
                    moves_str = moves_str.replace(matchbox[10], '', 1)
                    if moves_str == '':
                        # reconstruct available moves from the stored state (first 9 chars)
                        moves = [str(i) for i in range(9) if int(matchbox[i])-1 == 0] # -1 to revert to original field values
                        moves_str = ''.join(moves)
                        print(f"Replenishing moves for matchbox {matchbox[0:10]} to {moves_str}")
                    self._db.update_moves(matchbox[0:9], moves_str) 
    