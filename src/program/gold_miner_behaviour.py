"""
Gold-diggers will prioritize building the shortest path to a goal card, aiming to reach the treasure efficiently.
If a player knows the location of the gold (through a map card or reliable information from another player),
they will actively try to construct a path to the gold card. Gold-diggers may use the information provided by other
players about goal cards to determine if they are sincere or lying. This can help them make inferences about the
other player's role. When distrustful of another player, suspecting them of being a saboteur, gold-diggers may
strategically use sabotage cards against them. Conversely, if gold-diggers trust another player, considering them a
fellow gold-digger, they may use a mend card to help them if they are under the effect of a sabotage card.
Gold-diggers can keep track of drawn and played cards to predict which path cards are remaining in the deck and the
hands of other players, guiding their decision-making process towards reaching the gold. However, there may be
additional uncertainty due to discarded cards. They may deploy the dynamite card to remove dead-ends from paths that
could potentially lead to the gold cards.
"""


def gold_miner_behaviour(game_state):
    return []
