def gather_conjurations(card):
    conjurations = card.conjurations if card.conjurations else []
    for conjuration in conjurations:
        conjurations = conjurations + gather_conjurations(conjuration)
    return conjurations


def gather_root_summons(card):
    if not card.summons:
        return [card]
    root_summons = []
    for summon in card.summons:
        root_summons = root_summons + gather_root_summons(summon)
    return root_summons
