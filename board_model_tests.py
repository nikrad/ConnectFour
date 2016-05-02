import unittest

from board_model import (
    Board,
    DiscType,
    GridColumnFullError,
    InvalidGridError,
)


class BoardTests(unittest.TestCase):
    def test_new_board(self):
        # New board from scratch
        grid = [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ]
        self.assertEqual(Board().grid, grid)

        # New board from existing grid
        grid = [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 2, 0, 0],
            [0, 2, 0, 0, 1, 0, 0],
            [0, 1, 0, 1, 2, 0, 1],
            [2, 2, 1, 2, 1, 0, 2],
        ]
        self.assertEqual(Board(grid).grid, grid)

        # Invalid grid: type tuple
        grid = tuple(range(7))
        with self.assertRaises(InvalidGridError):
            Board(grid)

        # Invalid grid: height isn't 7
        grid = range(5)
        with self.assertRaises(InvalidGridError):
            Board(grid)

        # Invalid grid: missing inner lists
        grid = range(7)
        with self.assertRaises(InvalidGridError):
            Board(grid)

        # Invalid grid: inner lists don't have valid width
        grid = [[1], [1], [1], [1], [1], [1], [1]]
        with self.assertRaises(InvalidGridError):
            Board(grid)

        # Invalid grid: bad disc values
        grid = [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [7, 0, 0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 2, 1, 2, 'a'],
        ]
        with self.assertRaises(InvalidGridError):
            Board(grid)

        # Invalid grid: gaps in columns
        grid = [
            [0, 0, 0, 0, 0, 0, 2],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 2, 0, 0],
            [0, 2, 1, 0, 1, 0, 0],
            [0, 1, 0, 1, 2, 0, 1],
            [2, 2, 1, 2, 1, 0, 2],
        ]
        with self.assertRaises(InvalidGridError):
            Board(grid)

        # Invalid grid: the difference between player 1's and player 2's disks is more than 1
        grid = [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 1, 0, 1],
            [1, 2, 1, 0, 1, 1, 2],
        ]
        with self.assertRaises(InvalidGridError):
            Board(grid)

    def test_drop_disc(self):
        board = Board()

        # Invalid column indices
        with self.assertRaises(AssertionError):
            board.drop_disc(-1, DiscType(1))

        with self.assertRaises(AssertionError):
            board.drop_disc(10, DiscType(1))

        # Invalid disc type
        with self.assertRaises(AssertionError):
            board.drop_disc(5, 1)

        # Discs drop to the bottom of the column
        board.drop_disc(0, DiscType(1))
        board.drop_disc(1, DiscType(2))
        board.drop_disc(6, DiscType(1))
        board.drop_disc(6, DiscType(2))
        board.drop_disc(3, DiscType(1))

        expected_grid = [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 2],
            [1, 2, 0, 1, 0, 0, 1],
        ]
        self.assertEqual(board.grid, expected_grid)

        # Column fills up
        for i in xrange(3):
            board.drop_disc(2, DiscType.PLAYER_1)
            board.drop_disc(2, DiscType.PLAYER_2)

        expected_grid = [
            [0, 0, 2, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 2, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 2, 0, 0, 0, 2],
            [1, 2, 1, 1, 0, 0, 1],
        ]
        self.assertEqual(board.grid, expected_grid)
        with self.assertRaises(GridColumnFullError):
            board.drop_disc(2, DiscType.PLAYER_1)

        # Can't modify the grid directly
        with self.assertRaises(AssertionError):
            board.grid = expected_grid

