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

        Uses a depth first search with a
        recursive backtracking maze generation algorithm
        """
        pos_x, pos_y = pos

        # return 0 if already visited
        if visited[pos_x][pos_y] != -1:
            return 0

        count = 0

        # add to count if is colour
        if board[pos_x][pos_y] == self.colour:
            count += 1
            visited[pos_x][pos_y] = 1
        else:
            visited[pos_x][pos_y] = 0
            return count

        # check if neighbour is a valid location
        left = pos_x >= 1
        right = pos_x <= len(board) - 2
        up = pos_y >= 1
        down = pos_y <= len(board) - 2

        # add neighbours to check
        neighbours = []
        if left:
            neighbours.append((pos_x - 1, pos_y))
        if right:
            neighbours.append((pos_x + 1, pos_y))
        if up:
            neighbours.append((pos_x, pos_y - 1))
        if down:
            neighbours.append((pos_x, pos_y + 1))

        # check each neighbour. Depth First
        for pos_new in neighbours:
            count += self._undiscovered_blob_size(pos_new, board, visited)

        return count

    def score(self, board: Block) -> int:

        current_score = 0

        flattened = board.flatten()

        visited = [[-1 for _ in range(len(flattened))] for _ in
                   range(len(flattened))]

        for x, item in enumerate(flattened):
            for y in range(len(item)):
                # if current position is unchecked, check it.
                # Since the recursive back-tracker algorithm
                # is exhaustive for all cells
                # two checks within the same blocks
                # is guaranteed to have the same
                # score
                if visited[x][y] == -1:
                    current_score = max(
                        self._undiscovered_blob_size((x, y),
                                                     flattened,
                                                     visited),
                        current_score)
        return current_score

    def description(self) -> str:
        """Return a description of this goal.
        """
        return "Create the biggest blob!"


class PerimeterGoal(Goal):
    """A Goal to place the most blocks of your color
    on the perimeter"""

    def score(self, board: Block) -> int:
        score = 0
        flat_block = board.flatten()
        block_diameter = len(flat_block)

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
        return "Get the most of your color on the edge of the board!"


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer'
        ],
        'max-attributes': 15
    })
