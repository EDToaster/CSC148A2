"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the player class hierarchy.
"""

import random
from typing import Optional
import pygame
from renderer import Renderer
from block import Block
from goal import Goal

TIME_DELAY = 600


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    renderer:
        The object that draws our Blocky board on the screen
        and tracks user interactions with the Blocky board.
    id:
        This player's number.  Used by the renderer to refer to the player,
        for example as "Player 2"
    goal:
        This player's assigned goal for the game.
    """
    renderer: Renderer
    id: int
    goal: Goal

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.renderer = renderer
        self.id = player_id
        renderer.display_goal(self)

    def make_move(self, board: Block) -> int:
        """Choose a move to make on the given board, and apply it, mutating
        the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.
        """
        raise NotImplementedError


class HumanPlayer(Player):
    """A human player.

    A HumanPlayer can do a limited number of smashes.

    === Public Attributes ===
    num_smashes:
        number of smashes which this HumanPlayer has performed
    === Representation Invariants ===
    num_smashes >= 0
    """
    # === Private Attributes ===
    # _selected_block
    #     The Block that the user has most recently selected for action;
    #     changes upon movement of the cursor and use of arrow keys
    #     to select desired level.
    # _level:
    #     The level of the Block that the user selected
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0

    # The total number of 'smash' moves a HumanPlayer can make during a game.
    MAX_SMASHES = 1

    num_smashes: int
    _selected_block: Optional[Block]
    _level: int

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        super().__init__(renderer, player_id, goal)
        self.num_smashes = 0

        # This HumanPlayer has done no smashes yet.
        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._selected_block = None

    def process_event(self, board: Block,
                      event: pygame.event.Event) -> Optional[int]:
        """Process the given pygame <event>.

        Identify the selected block and mark it as highlighted.  Then identify
        what it is that <event> indicates needs to happen to <board>
        and do it.

        Return
           - None if <event> was not a board-changing move (that is, if was
             a change in cursor position, or a change in _level made via
            the arrow keys),
           - 1 if <event> was a successful move, and
           - 0 if <event> was an unsuccessful move (for example in the case of
             trying to smash in an invalid location or when the player is not
             allowed further smashes).
        """
        # Get the new "selected" block from the position of the cursor
        block = board.get_selected_block(pygame.mouse.get_pos(), self._level)

        # Remove the highlighting from the old "_selected_block"
        # before highlighting the new one
        if self._selected_block is not None:
            self._selected_block.highlighted = False
        self._selected_block = block
        self._selected_block.highlighted = True

        # Since get_selected_block may have not returned the block at
        # the requested level (due to the level being too low in the tree),
        # set the _level attribute to reflect the level of the block which
        # was actually returned.
        self._level = block.level

        if event.type == pygame.MOUSEBUTTONDOWN:
            block.rotate(event.button)
            return 1
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if block.level != 0:
                    self._level -= 1
                return None

            elif event.key == pygame.K_DOWN:
                if len(block.children) != 0:
                    self._level += 1
                return None

            elif event.key == pygame.K_h:
                block.swap(0)
                return 1

            elif event.key == pygame.K_v:
                block.swap(1)
                return 1

            elif event.key == pygame.K_s:
                if self.num_smashes >= self.MAX_SMASHES:
                    print('Can\'t smash again!')
                    return 0
                if block.smash():
                    self.num_smashes += 1
                    return 1
                else:
                    print('Tried to smash at an invalid depth!')
                    return 0

    def make_move(self, board: Block) -> int:
        """Choose a move to make on the given board, and apply it, mutating
        the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.

        This method will hold focus until a valid move is performed.
        """
        self._level = 0
        self._selected_block = board

        # Remove all previous events from the queue in case the other players
        # have added events to the queue accidentally.
        pygame.event.clear()

        # Keep checking the moves performed by the player until a valid move
        # has been completed. Draw the board on every loop to draw the
        # selected block properly on screen.
        while True:
            self.renderer.draw(board, self.id)
            # loop through all of the events within the event queue
            # (all pending events from the user input)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 1

                result = self.process_event(board, event)
                self.renderer.draw(board, self.id)
                if result is not None and result > 0:
                    # un-highlight the selected block
                    self._selected_block.highlighted = False
                    return 0


class RandomPlayer(Player):
    """A Player that chooses from 5 random moves and
    executes it.
    This player has no intelligence

    === Public Attributes ===
    smash_available:
        is the smash move available to the player?
        (Assuming RandomPlayer is only allowed
        to smash once, like HumanPlayer)
    """

    smash_available: bool

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """

        super().__init__(renderer, player_id, goal)
        self.smash_available = True

    def make_move(self, board: Block) -> int:
        """Selects a random move and executes it on the board.
        Always returns 0: Successful
        """

        # select and highlight a random block
        selected_block = choose_random_block(board)
        selected_block.highlighted = True

        # draw with highlight
        self.renderer.draw(board, self.id)

        pygame.time.wait(TIME_DELAY)

        # add available moves
        available_actions = [
            "LEFT-RT", "RIGHT-RT", "VERT-SW", "HORI-SW"]

        # add SMASH if it is a valid move
        if self.smash_available and selected_block.level != 0:
            available_actions.append("SMASH")

        action = random.choice(available_actions)

        if action == "SMASH":
            # no need to check if valid move because
            # we guaranteed it already.
            selected_block.smash()
            self.smash_available = False

        # apply each move
        elif action == "RIGHT-RT":
            selected_block.rotate(1)
        elif action == "LEFT-RT":
            selected_block.rotate(3)
        elif action == "HORI-SW":
            selected_block.swap(0)
        elif action == "VERT-SW":
            selected_block.swap(1)

        # un-highlight and draw
        selected_block.highlighted = False
        self.renderer.draw(board, self.id)

        # Successful move
        return 0


class SmartPlayer(Player):
    """A Smart player generates multiple (based on difficulty level) moves
    and selects the highest scoring move.

    === Public Attributes ===
    difficulty_level:
        The difficulty level for the smart player.
        This influences the number of iterations
        when deciding a move
    """
    difficulty_level: int

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal,
                 difficulty_level: int) -> None:
        super().__init__(renderer, player_id, goal)
        self.difficulty_level = difficulty_level

    def make_move(self, board: Block):
        num_moves: int = \
            5 if self.difficulty_level == 0 else \
            10 if self.difficulty_level == 1 else \
            25 if self.difficulty_level == 2 else \
            50 if self.difficulty_level == 3 else \
            100 if self.difficulty_level == 4 else \
            150

        best_score: int = -1
        best_action: tuple
        best_block: Block

        for _ in range(num_moves):
            random_block: Block = choose_random_block(board)
            # add available moves based on random_block
            available_actions = \
                [
                    (random_block.rotate, 1),
                    (random_block.rotate, 3),
                    (random_block.swap, 0),
                    (random_block.swap, 1)
                ]

            choice = random.randint(0, 3)
            action = available_actions[choice]

            # get inverse choice to undo later
            # if choice is rotate, pick other rotate to undo
            # if choice is swap, swap again to undo
            inverse_choice = \
                0 if choice == 1 else\
                1 if choice == 0 else\
                choice
            inverse_action = available_actions[inverse_choice]

            # execute the specified action
            action[0](action[1])

            current_score = self.goal.score(board)
            if current_score > best_score:
                best_action = action
                best_block = random_block

            # execute inverse action
            inverse_action[0](inverse_action[1])

        # Highlight and draw
        best_block.highlighted = True
        self.renderer.draw(board, self.id)

        pygame.time.wait(TIME_DELAY)

        # Do best move
        best_action[0](best_action[1])

        # Un-highlight and draw
        best_block.highlighted = False
        self.renderer.draw(board, self.id)


def choose_random_block(board: Block) -> Block:
    """Chooses a random block from the board, excluding
    useless moves.
    """
    # This function does not simply pick a random block,
    # the algorithm was adjusted to exclude some but not all useless moves,
    # in order to make the random plays seem more "organic"
    #
    # The function will never select the deepest block, even though some useless
    # moves will still be done. Some blocks are intentionally and indirectly
    # prioritized.

    action = random.randint(0, 4)

    if action == 4 or not board.children:
        if not hasattr(board, "parent"):
            # We don't want the "root block" to be picked very often,
            # makes it look boring
            return board.children[random.randint(0, 3)]
        else:
            # this allows the "root block" to still be picked some times
            return board.parent
    else:
        return choose_random_block(board.children[action])


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer',
            'pygame'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
