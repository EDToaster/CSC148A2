"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the Goal class hierarchy.
"""

from typing import List, Tuple
from block import Block


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class BlobGoal(Goal):
    """A goal to create the largest connected blob of this goal's target
    colour, anywhere within the Block.
    """

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
           -1  if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """

        current = pos
        stack = [None]
        count = 0
        if board[pos[0]][pos[1]] != self.colour:
            return count
        while current is not None:
            x = current[0]
            y = current[1]
            stack.append(current)
            if visited[x][y] == -1:
                count += 1
            visited[x][y] = 1

            if y >= 1 and visited[x][y - 1] == -1 and board[x][y - 1] == self.colour:
                current = (x, y - 1)
            elif y <= len(board) - 2 and visited[x][y + 1] == -1 and board[x][y + 1] == self.colour:
                current = (x, y + 1)
            elif x >= 1 and visited[x - 1][y] == -1 and board[x - 1][y] == self.colour:
                current = (x - 1, y)
            elif x <= len(board) - 2 and visited[x + 1][y] == -1 and board[x + 1][y] == self.colour:
                current = (x + 1, y)
            else:
                stack.pop()
                current = stack.pop()

        return count




        # stack = [None]
        #
        # current = pos
        #
        # count = 0
        #
        # while current is not None:
        #     x = pos[0]
        #     y = pos[1]
        #
        #     stack.append(current)
        #
        #     if board[x][y] == self.colour:
        #         if visited[x][y] == -1:
        #             count += 1
        #         visited[x][y] = 1
        #
        #         if y > 0 \
        #                 and visited[x][y - 1] == -1 \
        #                 and board[x][y - 1] == self.colour:
        #             current = (x, y - 1)
        #         elif y < len(board[0]) - 1 \
        #                 and visited[x][y + 1] == -1 \
        #                 and board[x][y + 1] == self.colour:
        #             current = (x, y + 1)
        #         elif x > 0 \
        #                 and visited[x - 1][y] == -1 \
        #                 and board[x - 1][y] == self.colour:
        #             current = (x - 1, y)
        #         elif x < len(board) - 1 \
        #                 and visited[x + 1][y] == -1 \
        #                 and board[x + 1][y] == self.colour:
        #             current = (x + 1, y)
        #         else:
        #             current = stack.pop()
        #     else:
        #         visited[x][y] = 0
        #         current = stack.pop()
        # return count

    def score(self, board: Block) -> int:

        current_score = 0

        flattened = board.flatten()
        for x, item in enumerate(flattened):
            for y in range(len(item)):
                visited = [[-1 for i in range(len(flattened))] for j in
                           range(len(flattened))]
                current_score = max(self._undiscovered_blob_size((x, y), flattened, visited), current_score)
        return current_score

    def description(self) -> str:
        """Return a description of this goal.
        """
        return "Create the biggest blob"


class PerimeterGoal(Goal):
    """"""

    def _undiscovered_perimeter_size(self) -> int:
        """
        """
        pass

    def score(self, board: Block) -> int:
        score = 0
        flat_block = board.flatten()
        block_diameter = len(flat_block)
        scores = [0, 0, 0, 0]

        for i in range(block_diameter):
            if flat_block[0][i] == self.colour:
                score += 1

            if flat_block[i][0] == self.colour:
                score += 1

            if flat_block[block_diameter - 1][i] == self.colour:
                score += 1

            if flat_block[i][block_diameter - 1] == self.colour:
                score += 1

        return score

    def description(self) -> str:
        """Return a description of this goal.
        """
        return "Get the most of your colour, on the outer edges of the game board"


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer'
        ],
        'max-attributes': 15
    })
