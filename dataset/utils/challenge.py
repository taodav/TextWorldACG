"""
.. _the_cook:

The Cook
========

This game takes place in a typical house and consists in
finding the right food item and cooking it.
Here's the map of the house.

::
                Bathroom
                    +
                    |
                    +
    Bedroom +--+ Kitchen +----+ Backyard
                    +              +
                    |              |
                    +              +
               Living Room       Garden

"""

from typing import Mapping, Union, Dict, Optional


import textworld
from textworld import GameOptions
from textworld.logic import Proposition

from textworld.utils import encode_seeds


def make_game_from_level(level: int, options: Optional[GameOptions] = None) -> textworld.Game:
    """ Make a Cooking game of the desired difficulty level.

    Arguments:
        level: Difficulty level (see notes).
        options:
            For customizing the game generation (see
            :py:class:`textworld.GameOptions <textworld.generator.game.GameOptions>`
            for the list of available options).

    Returns:
        Generated game.

    Notes:
        Difficulty levels are defined as follows:
        TODO
    """
    if level == 1:
        mode = "easy"
    elif level == 2:
        mode = "medium"
    elif level == 3:
        mode = "hard"
    else:
        raise ValueError("Only level 1, 2 or 3 is supported for this game.")

    return make_game(mode, options)

def make_game(mode: str, options: GameOptions) -> textworld.Game:
    """ Make a The Cook game.

    Arguments:
        mode: Mode for the game
              TODO
        options:
            For customizing the game generation (see
            :py:class:`textworld.GameOptions <textworld.generator.game.GameOptions>`
            for the list of available options).

    Returns:
        Generated game.
    """
    metadata = {}  # Collect infos for reproducibility.
    metadata["desc"] = "Cooking"
    metadata["mode"] = mode
    metadata["seeds"] = options.seeds
    metadata["world_size"] = 6
    metadata["quest_length"] = None  # TBD

    rngs = options.rngs
    rng_map = rngs['map']
    rng_objects = rngs['objects']
    rng_grammar = rngs['grammar']
    rng_quest = rngs['quest']

    # Make the generation process reproducible.
    textworld.g_rng.set_seed(2018)

    M = textworld.GameMaker()
    M.grammar = textworld.generator.make_grammar(options.grammar, rng=rng_grammar)

    # Start by building the layout of the world.
    bedroom = M.new_room("bedroom")
    kitchen = M.new_room("kitchen")
    livingroom = M.new_room("living room")
    bathroom = M.new_room("bathroom")
    backyard = M.new_room("backyard")
    garden = M.new_room("garden")

    # Connect rooms together.
    bedroom_kitchen = M.connect(bedroom.east, kitchen.west)
    kitchen_bathroom = M.connect(kitchen.north, bathroom.south)
    kitchen_livingroom = M.connect(kitchen.south, livingroom.north)
    kitchen_backyard = M.connect(kitchen.east, backyard.west)
    backyard_garden = M.connect(backyard.south, garden.north)

    # Add doors.
    bedroom_kitchen.door = M.new(type='d', name='wooden door')
    kitchen_backyard.door = M.new(type='d', name='screen door')

    kitchen_backyard.door.add_property("closed")

    # Design the bedroom.
    drawer = M.new(type='c', name='chest drawer')
    trunk = M.new(type='c', name='antique trunk')
    bed = M.new(type='s', name='king-size bed')
    bedroom.add(drawer, trunk, bed)

    # Close the trunk and drawer.
    trunk.add_property("closed")
    drawer.add_property("closed")

    # - The bedroom's door is locked
    bedroom_kitchen.door.add_property("locked")

    # - Describe the room.
    # bedroom.desc = ""

    # Design the kitchen.
    counter = M.new(type='s', name='counter')
    stove = M.new(type='stove', name='stove')
    kitchen_island = M.new(type='s', name='kitchen island')
    refrigerator = M.new(type='c', name='refrigerator')
    kitchen.add(counter, stove, kitchen_island, refrigerator)

    # - Add some food in the refrigerator.
    apple = M.new(type='f', name='apple')
    milk = M.new(type='f', name='milk')
    refrigerator.add(apple, milk)

    # Design the bathroom.
    toilet = M.new(type='c', name='toilet')
    sink = M.new(type='s', name='sink')
    bath = M.new(type='c', name='bath')
    bathroom.add(toilet, sink, bath)

    toothbrush = M.new(type='o', name='toothbrush')
    sink.add(toothbrush)
    soap_bar = M.new(type='o', name='soap bar')
    bath.add(soap_bar)

    # Design the living room.
    couch = M.new(type='s', name='couch')
    low_table = M.new(type='s', name='low table')
    tv = M.new(type='s', name='tv')
    livingroom.add(couch, low_table, tv)

    remote = M.new(type='o', name='remote')
    low_table.add(remote)
    bag_of_chips = M.new(type='f', name='half of a bag of chips')
    couch.add(bag_of_chips)

    # Design backyard.
    bbq = M.new(type='s', name='bbq')
    patio_table = M.new(type='s', name='patio table')
    chairs = M.new(type='s', name='set of chairs')
    backyard.add(bbq, patio_table, chairs)

    # Design garden.
    shovel = M.new(type='o', name='shovel')
    tomato = M.new(type='f', name='tomato plant')
    carrot = M.new(type='f', name='carrot')
    lettuce = M.new(type='f', name='lettuce')
    garden.add(shovel, tomato, carrot, lettuce)

    # Close all containers
    for container in M.findall(type='c'):
        container.add_property("closed")

    # Set uncooked property for to all food items.
    foods = M.findall(type='f')
    for food in foods:
        food.add_property("edible")
        food.add_property("raw")

    # Shuffle the position of the food items.
    food_names = [food.name for food in foods]
    rng_quest.shuffle(food_names)
    for food, name in zip(foods, food_names):
        food.orig_name = food.name
        food.name = name

    # The player starts in the bedroom.
    M.set_player(bedroom)

    # Quest
    walkthrough = []

    # Part I - Escaping the room.
    # Generate the key that unlocks the bedroom door.
    bedroom_key = M.new(type='k', name='old key')
    M.add_fact("match", bedroom_key, bedroom_kitchen.door)

    # Decide where to hide the key.
    if rng_quest.rand() > 0.5:
        drawer.add(bedroom_key)
        walkthrough.append("open chest drawer")
        walkthrough.append("take old key from chest drawer")
    else:
        trunk.add(bedroom_key)
        walkthrough.append("open antique trunk")
        walkthrough.append("take old key from antique trunk")

    # Unlock the door, open it and leave the room.
    walkthrough.append("unlock wooden door with old key")
    walkthrough.append("open wooden door")
    walkthrough.append("go east")

    # Part II - Find food item.
    # 1. Randomly pick a food item to cook.
    food = rng_quest.choice(foods)

    # Retrieve the food item and get back in the kitchen.
    # HACK: handcrafting that part.
    if food.orig_name in ["apple", "milk"]:
        walkthrough.append("open refrigerator")
        walkthrough.append("take {} from refrigerator".format(food.name))
    elif food.orig_name == "half of a bag of chips":
        walkthrough.append("go south")
        walkthrough.append("take {} from couch".format(food.name))
        walkthrough.append("go north")
    elif food.orig_name in ["carrot", "lettuce", "tomato plant"]:
        walkthrough.append("open screen door")
        walkthrough.append("go east")
        walkthrough.append("go south")
        walkthrough.append("take {}".format(food.name))
        walkthrough.append("go north")
        walkthrough.append("go west")

    # Part II - Cooking the food item.
    walkthrough.append("put {} on stove".format(food.name))
    walkthrough.append("cook {}".format(food.name))
    # walkthrough.append("eat {}".format(food.name))

    # 2. Determine the winning condition(s) of the game.
    winning_conditions = [Proposition("cooked", [food.var])]
    # quest = M.set_quest_from_final_state(winning_conditions)
    quest = M.set_quest_from_commands(walkthrough)

    # 3. Determine the losing condition(s) of the game.
    quest.set_failing_conditions([Proposition("eaten", [food.var]),
                                  Proposition("raw", [food.var])])

    # - Add a hint of what needs to be done in this game.
    objective = "The dinner is almost ready! It's only missing a grilled {}."
    objective = objective.format(food.name)
    note = M.new(type='o', name='note', desc=objective)
    kitchen_island.add(note)

    game = M.build()
    if mode == "easy":
        # Use the detailed version of the objective.
        pass
    elif mode == "medium":
        # Use a very high-level description of the objective.
        game.quests[0].desc = objective
    elif mode == "hard":
        # No description of the objective.
        game.quests[0].desc = ""
    else:
        raise ValueError("Unknown mode: {}.".format(mode))

    game.metadata = metadata
    uuid = "tw-cook-{specs}-{flags}-{seeds}"
    uuid = uuid.format(specs=mode,
                       flags=options.grammar.uuid,
                       seeds=encode_seeds([options.seeds[k] for k in sorted(options.seeds)]))
    game.metadata["uuid"] = uuid
    return game


# Register the Cook challenge
from textworld.challenges import CHALLENGES
CHALLENGES['cooking'] = make_game_from_level
