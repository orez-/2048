import random

LEFT, DOWN, RIGHT, UP = range(4)


class Human(object):
    """
    Isn't a bot at all????????
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
    """
    def __init__(self):
        self.current = 0

    def get_action(self, board):
        self.current = (self.current + 1) % 4
        print ["LEFT", "DOWN", "RIGHT", "UP"][self.current]
        return self.current


class Insistent(object):
    """
    Insistent bot will keep trying one way. Once that way isn't valid,
    tries a new way.
    """
    def __init__(self):
        self.direction = 0

    def get_action(self, board):
        if not board.try_move(self.direction):
            self.direction = random.randint(0, 3)
        return self.direction


class Tetris(object):
    """
    Tetris bot never presses up.
    """
    def __init__(self):
        pass

    def get_action(self, board):
        # return self.quick_look(board)
        return self.bfs(board, 1000)

    def quick_look(self, board):
        best = (UP, 1)
        for dr in (DOWN, LEFT, RIGHT):
            result = board.try_move(dr)
            if result is not False:
                score = self.score(result)
                if score > best[1]:
                    best = (dr, score)
        return best[0]


    def bfs(self, board, depth):
        best = (UP, 0)
        actions = []
        for dr in (DOWN, LEFT, RIGHT):
            result = board.try_move(dr)
            if result is not False:
                score = self.score(result)
                actions.append((dr, score, result))
                if score > best[1]:
                    best = (dr, score)
        if not actions:
            return UP

        for _ in xrange(depth):
            actions.sort(key=lambda (_, s, __): -s)
            if not actions:
                return best[0]
            dr, score, board_state = actions.pop(0)
            if score > best[1]:
                best = (dr, score)
            for _ in (DOWN, LEFT, RIGHT):
                result = board_state.try_move(dr)
                if result is not False:
                    actions.append((dr, self.score(result), result))
        return actions.pop(0)[0]

    def score(self, board):
        score = 10000
        if board.lost:
            return -float("inf")
        if board.won:
            return float("inf")
        tmp_board = [[0 if elem is None else 2 ** elem
            for elem in row] for row in board.board]
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
