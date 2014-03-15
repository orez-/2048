import random

LEFT, DOWN, RIGHT, UP = range(4)


class Human(object):
    """
    Isn't a bot at all????????

    Best score: ????
    Worst score: ????
    """
    def get_action(self, board):
        inp = raw_input("> ")
        try:
            inp = ["LEFT", "DOWN", "RIGHT", "UP"].index(inp.upper())
        except:
            pass
        return inp


class Tumbler(object):
    """
    Spins around. Isn't very good.

    Best score: 256 (7)
    Worst score: 64 (5)
    """
    def __init__(self):
        self.current = 0

    def get_action(self, board):
        self.current = (self.current + 1) % 4
        return self.current


class Insistent(object):
    """
    Insistent bot will keep trying one way. Once that way isn't valid,
    tries a new way.

    Best score: 64 (5)
    Worst score: 32 (4)
    """
    def __init__(self):
        self.direction = 0

    def get_action(self, board):
        if not board.try_move(self.direction):
            self.direction = random.randint(0, 3)
        return self.direction


class Pendulum(object):
    """
    Pendulum swings back and forth between RIGHT and LEFT. Never goes UP.

    Best score: 256 (7)
    Worst score: Infinite loop
    """
    def __init__(self):
        self.direction = 0

    def get_action(self, board):
        if self.direction == 3:
            self.direction = 0
            return 1
        self.direction += 1
        return self.direction - 1


class Tetris(object):
    """
    Tetris bot never presses up.

    Best score: 1024 (9)
    Worst score: 256 (7)
    """
    def get_action(self, board):
        return self.one_step_average(board)

    def quick_look(self, board):
        """
        Get the move that results in the best known result one turn
        in the future.
        """
        best = (UP, 1)
        for dr in (DOWN, LEFT, RIGHT):
            result = board.try_move(dr)
            if result is not False:
                score = self.score(result)
                if score > best[1]:
                    best = (dr, score)
        return best[0]

    def one_step_average(self, board):
        """
        Get the move that results in the best expected result one turn
        in the future, based on where the random piece could land.
        """
        best = (UP, 1)
        for dr in (DOWN, LEFT, RIGHT):
            result = board.try_move(dr)
            if result is not False:
                score = 0
                two, four = self.possible_configs(result)
                over = len(two)
                score += sum((self.score(b) * 0.9 for b in two))
                score += sum((self.score(b) * 0.1 for b in four))
                score /= over
                if score > best[1]:
                    best = (dr, score)
        return best[0]

    def possible_configs(self, board):
        """
        Given a board, get all possible boards that could result once
        the random piece is placed.
        """
        twos = []
        fours = []
        for (x, y) in board.open_spots:
            for lst, num in zip((twos, fours), (0, 1)):
                b = board.clone()
                b.board[y][x] = num
                lst.append(b)
        return twos, fours

    def score(self, board):
        """
        Heuristic that values keeping things ordered from top to bottom
        and horizontally (with more emphasis on lower rows), and
        having more spaces open (making more matches).
        """
        score = 10000
        if board.lost:
            return 0
        if board.won:
            return 200000
        tmp_board = [
            [0 if elem is None else 2 ** elem for elem in row]
            for row in board.board]
        for row, (above, below) in enumerate(zip(tmp_board, tmp_board[1:])):
            if max(above) < max(below):  # favor bigger numbers below
                score += (max(below) - max(above)) * (2 ** row)
            if min(above) < min(below):  # favor smaller numbers above
                score += (min(below) - min(above)) * (4 ** row)
            if sum(above) < sum(below):  # favor a lower average higher
                score += ((sum(below) - sum(above)) / 4) * (2 ** row)
            # favor rows to be ordered
            if sorted(below) == below or sorted(below, key=lambda q: -q) == below:
                score += max(below) * (3 ** row)
        # favor more blank spaces (make more matches!)
        score += sum(map(lambda row: row.count(0), tmp_board)) * 1000
        return score


class TetrisPlanner(Tetris):
    """
    A smarter Tetris that thinks ahead.

    Best score: Won!
    Worst score: 512 (8)
    """
    def get_action(self, board):
        return self.average_lookahead(board)

    def average_lookahead(self, original_board):
        """
        Look a few steps ahead to decide the statistically best move,
        counting the random piece placement.
        """
        lookup = {}
        frontier = [original_board]
        board_num_cutoff = 1000
        while board_num_cutoff >= 0:
            new_frontier = []
            # If the entire game's mapped out, stop looking.
            if not frontier:
                break
            for source_board in frontier:
                if source_board in lookup:
                    continue
                lookup[source_board] = {}
                # predict movement in all directions
                for dr in (DOWN, LEFT, RIGHT):
                    tried_board = source_board.try_move(dr)
                    if tried_board is not False:
                        twos, fours = self.possible_configs(tried_board)
                        new_frontier += twos + fours  # try these next
                        confs = (
                            map(lambda q: (0.9, q), twos) +
                            map(lambda q: (0.1, q), fours))
                        lookup[source_board][dr] = confs
                        board_num_cutoff -= len(confs)
            frontier = new_frontier
        # figure out the best direction to go
        return self.rec_best(original_board, lookup)[0]

    def rec_best(self, board, lookup, mult=1):
        """
        Given the lookup map, recursively find the best move to make.
        """
        best_score = 1
        direction = UP
        if board not in lookup:  # just take the estimated score
            return (-1, self.score(board) * mult)
        for dr, confs in lookup[board].items():
            score = sum(
                (self.rec_best(new_board, lookup, mlt)[1]
                    for mlt, new_board in confs)) * 2 / len(confs)
            if score > best_score:
                best_score = score
                direction = dr
        return (direction, best_score)
