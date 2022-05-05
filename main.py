import random

from janggi_game import JanggiGame
from classes.camp import Camp
from classes.formation import Formation

if __name__ == '__main__':
    camp = Camp(random.randint(0, 1))
    choFormation = Formation(random.randint(1, 4))
    hanFormation = Formation(random.randint(1, 4))
    game = JanggiGame(camp, choFormation, hanFormation)
    print(f"CHO: {game.choScore} / HAN: {game.hanScore}")
    print(game.board)
