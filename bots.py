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
