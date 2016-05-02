from enum import Enum


class BoardException(Exception):
    pass


class InvalidGridError(BoardException):
    pass


class GridColumnFullError(BoardException):
    pass


class DiscType(Enum):
    """ Enum type for the board's disc values. """
    NONE = 0
    PLAYER_1 = 1
    PLAYER_2 = 2


PLAYABLE_DISK_TYPES = frozenset([
    DiscType.PLAYER_1,
    DiscType.PLAYER_2,
])


# TODO(nikrad): add docstrings to `Board` methods
# TODO(nikrad): add tests for `is_winning_disc()` and `is_full()`

class Board(object):
    WIDTH = 7
    HEIGHT = 6

    def __init__(self, grid=None):
        if grid is None:
            self.grid = self._new_grid()
        else:
            self.grid = grid

    @property
    def grid(self):
        return self._grid

    @grid.setter
    def grid(self, value):
        if hasattr(self, '_grid'):
            assert False, "Don't update the board grid directly; instead use the instance method `drop_disc()`"
        else:
            self._validate_grid(value)
            self._grid = value

    def drop_disc(self, column_index, disc_type):
        """Drop a disc in a column slot.

        Args:
            column_index (int): index of the column in which to drop a disc
            disc_type (DiscType): disc type that should be dropped

        Returns:

        """
        column_index = int(column_index)
        assert column_index > -1, "Column index must be between 0 and 6. Got: %d" % column_index
        assert column_index < self.WIDTH, "Column index must be between 0 and 6. Got: %d" % column_index
        assert disc_type in PLAYABLE_DISK_TYPES, "Only disc types in %s can be dropped" % PLAYABLE_DISK_TYPES

        # Walk upward from the bottom position in the column and find the first empty spot. If we walk past top row,
        # the column is full.
        row_index = self.HEIGHT - 1
        while row_index > -1:
            if self.grid[row_index][column_index] == DiscType.NONE.value:
                self.grid[row_index][column_index] = disc_type.value
                return (row_index, column_index)

            row_index -= 1

        raise GridColumnFullError()

    def is_winning_disc(self, last_disc_row_index, last_disc_column_index):
        """Check if this disc leads to a victory.

        Args:
            last_disc_row_index (int): row index of the dropped disc
            last_disc_column_index (int): column index of the dropped disc

        Returns:
            If the disc leads to a victory for player in position X, it returns the player's position
            integer (i.e. X). If this disc doesn't lead to a victory, it returns None.
        """
        def four_in_a_row(values):
            if len(set(values)) == 1 and values[0] > 0:
                return values[0]

            return None

        # TODO(nikrad): Add explanations of the win-checking logic

        # Check for horizontal win
        leftmost_win_start_index = max(0, last_disc_column_index - 3)
        rightmost_win_start_index = min(3, last_disc_column_index)
        for left_index in xrange(leftmost_win_start_index, rightmost_win_start_index + 1):
            right_index = left_index + 4
            values = self.grid[last_disc_row_index][left_index:right_index]
            winner = four_in_a_row(values)
            if winner:
                return winner

        # Check for vertical win if the last disc was in rows 0 - 2
        if last_disc_row_index < 3:
            bottom_index = last_disc_row_index + 4
            values = [self.grid[i][last_disc_column_index] for i in xrange(last_disc_row_index, bottom_index)]
            winner = four_in_a_row(values)
            if winner:
                return winner

        # Check for diagonal \ win
        if ((last_disc_column_index - last_disc_row_index) < 4 and last_disc_row_index - last_disc_column_index < 3):
            # It's possible this disc creates a win if we check from a start position higher along the disc's diagonal
            furthest_possible_diagonal_win = min(3, last_disc_row_index, last_disc_column_index)
            nearest_possible_diagonal_win = max(0, last_disc_column_index - 3, last_disc_row_index - 2)
            # Double check if we can include the last move's disc position as a start position
            for distance in xrange(nearest_possible_diagonal_win, furthest_possible_diagonal_win + 1):
                row_index = last_disc_row_index - distance
                column_index = last_disc_column_index - distance
                values = [self.grid[row_index + i][column_index + i] for i in xrange(4)]
                winner = four_in_a_row(values)
                if winner:
                    return winner

        # Check for diagonal / win
        sum_of_last_move_indices = (last_disc_row_index + last_disc_column_index)
        if sum_of_last_move_indices > 2 and sum_of_last_move_indices < 9:
            # It's possible this disc creates a win if we check from a start position higher along the disc's diagonal
            furthest_possible_diagonal_win = min(3, last_disc_row_index, self.WIDTH - last_disc_column_index - 1)
            nearest_possible_diagonal_win = max(0, last_disc_row_index - 2, 3 - last_disc_column_index)
            for distance in xrange(nearest_possible_diagonal_win, furthest_possible_diagonal_win + 1):
                row_index = last_disc_row_index - distance
                column_index = last_disc_column_index + distance
                values = [self.grid[row_index + i][column_index - i] for i in xrange(4)]
                winner = four_in_a_row(values)
                if winner:
                    return winner

        return None

    def is_full(self):
        """Check if a board is full.

        Returns:
            True if there are no empty spots on the board, otherwise False
        """
        for row in self.grid:
            if not all(row):
                return False

        return True

    def _new_grid(self):
        return [[DiscType.NONE.value for _ in xrange(self.WIDTH)] for _ in xrange(self.HEIGHT)]

    def _validate_column_values(self, transposed_grid):
        # Check every slot for gaps and validate each slot's values
        player_1_values = 0
        player_2_values = 0

        for column_index, column in enumerate(transposed_grid):
            # To walk upward from the bottom row in a column, we start at the end of the list
            row_index = len(column) - 1
            while row_index > -1:
                # Validate grid value
                value = column[row_index]
                try:
                    disc_type = DiscType(value)
                except ValueError:
                    raise InvalidGridError(
                        "Disc value %s in grid row %d and column %d isn't valid" % (value, row_index, column_index)
                    )

                if disc_type == DiscType.NONE:
                    # All column values above (i.e. before) this should be DiscType.NONE
                    if column[:row_index] != [DiscType.NONE.value] * row_index:
                        raise InvalidGridError("Gap found in column %d" % column_index)

                if disc_type == DiscType.PLAYER_1:
                    player_1_values += 1
                elif disc_type == DiscType.PLAYER_2:
                    player_2_values += 1

                row_index -= 1

        # Ensure that neither player has more than 1 extra disc on the board than the other player does
        if abs(player_1_values - player_2_values) > 1:
            raise InvalidGridError("Player 1 and Player 2 disc counts vary by more than 1")


    def _validate_grid(self, grid):
        # Check grid type
        if not isinstance(grid, list):
            raise InvalidGridError("Grid must be of type `list`")

        # Check grid height
        if len(grid) != self.HEIGHT:
            raise InvalidGridError("Grid height must be %d" % self.HEIGHT)

        for row_index, row in enumerate(grid):
            # Check grid row type
            if not isinstance(row, list):
                raise InvalidGridError("Grid rows must be of type `list`")

            # Check grid row width
            if len(row) != self.WIDTH:
                raise InvalidGridError("Grid width must be %d" % self.WIDTH)

        transposed_grid = [list(column) for column in zip(*grid)]
        self._validate_column_values(transposed_grid)
