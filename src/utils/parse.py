import re

def parse_game_state(game_state, EOS_token='<EOS>'):
    """
    parses game state and returns the parsed state, along with all admissible commands
    for that state
    :param game_state:
    :return: state, actions
    """
    state = game_state.description.replace('\n', ' ')
    inventory = game_state.inventory.replace('\n', ' ')
    actions = []
    for action in game_state.admissible_commands:
        if action != 'inventory' and action != 'look':
            action_with_eos = action.lower() + ' ' + EOS_token
            actions.append(action_with_eos)
    return [state, inventory, actions]

def get_state_entities(all_entities, state_input):
    entities = []
    for ent, type in all_entities:
        reword = '\s' + ent + '\W'
        regexp = re.compile(reword)
        if regexp.search(state_input):
            entities.append((ent, type))

    for direction in ['north', 'east', 'south', 'west']:
        if direction in state_input:
            entities.append((direction, 'direction'))
    return entities