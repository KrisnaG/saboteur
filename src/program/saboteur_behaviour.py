"""
Saboteurs will aim to construct long paths with numerous turns, unnecessary crossroads, or delay path construction
through various means. This tactic may lead to lower trust among gold-diggers towards the saboteur if employed
excessively. If a saboteur knows the location of the gold, they will actively sabotage any attempt made by
gold-diggers to reach the gold card. Saboteurs may analyze information provided by other players about goal cards to
determine if they are sincere or lying, enabling them to make inferences about the other player's role. When
suspecting another player of being a gold-digger, saboteurs may choose to use sabotage cards against them. However,
doing so when other gold-diggers have no reason to doubt the player's intentions may backfire and lead to retaliation
from gold-diggers. They may decide to block paths or destroy path cards using the dynamite card strategically.
However, doing so may raise suspicions among gold-diggers, possibly identifying the player as a saboteur.
"""
import random

from src.environment.saboteur_environment import SaboteurEnvironment


def saboteur_behaviour(game_state, kb):
    action = []
    legal_actions = SaboteurEnvironment.get_legal_actions(game_state)
    action.append(random.choice(legal_actions))
    return action
