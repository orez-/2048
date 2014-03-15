import random


class Board(object):
    def __init__(self, other_board=None):
        if other_board:
            if isinstance(other_board, Board):
                other_board = other_board.board
            self.board = map(list, other_board)
        else:
            self.board = [[None] * 4 for _ in xrange(4)]
            self.add_piece()
            self.add_piece()

    def clone(self):
        return Board(self)

    @property
    def open_spots(self):
        for y, row in enumerate(self.board):
            for x, elem in enumerate(row):
                if elem is None:
                    yield (x, y)

    def add_piece(self):
        x, y = random.choice(list(self.open_spots))
        self.board[y][x] = 0 if random.randint(0, 9) else 1

    def __str__(self):
        def stringify(elem):
            if elem is None:
                return '.'
            elif elem == 10:
                return 'A'
            return str(elem)
        return '\n'.join((''.join(map(stringify, row)) for row in self.board))

    def try_move(self, direction):
        old_board = self.board

        # Spin the board
        for _ in xrange(direction):
            old_board = zip(*old_board[::-1])

        new_board = []
        for row in old_board:
            new_row = []
            combined = False
            for elem in row:
                if elem is None:
                    continue
                if new_row and new_row[-1] == elem and not combined:
                    new_row[-1] += 1
                    combined = True
                else:
                    new_row.append(elem)
                    combined = False
            new_row.extend([None] * (4 - len(new_row)))
            new_board.append(new_row)

        # Spin the board back.
        for _ in xrange(direction):
            new_board = zip(*new_board)[::-1]

        if map(list, new_board) == self.board:
            return False

        return Board(new_board)

    @property
    def lost(self):
        if self.won:
            return False
        for direction in xrange(4):
            if self.try_move(direction):
                return False
        return True

    @property
    def won(self):
        for row in self.board:
            for elem in row:
                if elem == 10:
                    return True
        return False

    @property
    def game_over(self):
        return self.lost or self.won

    def move(self, direction, add_piece=True):
        result = self.try_move(direction)
        if result is False:
            return (self, False)
        if add_piece:
            result.add_piece()
        return (result, True)

    def __eq__(self, other):
        return self.board == other.board


class Game(object):
    def __init__(self, input_method):
        self.input_method = input_method

    def play(self):
        input_method = self.input_method()
        board = Board()
        while not board.game_over:
            print board, "\n"
            action = input_method.get_action(Board(board))
            try:
                action = int(action) % 4
            except ValueError:
                print "Invalid input"
            else:
                board, success = board.move(action)

        print board, "\n"
        print "Game Over"

    def performance_test(self, runs=25):
        import sys
        import time

        results = {}
        timings = []
        try:
            for i in xrange(runs):
                sys.stdout.write("\rRunning test %s" % i)
                sys.stdout.flush()
                input_method = self.input_method()
                board = Board()
                timeout_counter = 10
                start = time.time()
                while not board.game_over:
                    try:
                        action = input_method.get_action(Board(board))
                    except Exception:
                        results.setdefault("Error", 0)
                        results["Error"] += 1
                        break
                    try:
                        action = int(action) % 4
                    except ValueError:
                        timeout_counter -= 1
                    else:
                        board, success = board.move(action)
                        if success:
                            timeout_counter = 10
                        else:
                            timeout_counter -= 1
                    if timeout_counter <= 0:
                        results.setdefault("Timeout", 0)
                        results["Timeout"] += 1
                        break
                else:  # didn't break
                    highest_num = max(map(max, board.board))
                    results.setdefault(highest_num, 0)
                    results[highest_num] += 1
                timings.append(time.time() - start)
        except KeyboardInterrupt:
            print "\nAborting",
        if results:
            print "\nResults\n======="
            print '\n'.join(map(lambda res: "%s: %s" % res, sorted(results.iteritems())))
            print "\nTimes (s)\n========="
            print "Min:", min(timings)
            print "Avg:", sum(timings) / len(timings)
            print "Max:", max(timings)
        print
