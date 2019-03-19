import sys
import textworld
import textworld.challenges
import random
import argparse
from tqdm import tqdm

from src.utils import challenge


def _get_available_challenges():
    challenges = []
    for challenge in textworld.challenges.CHALLENGES:
        challenges.append("tw-{}-level{{N}}".format(challenge))

    return challenges

def exit_listing_challenges(challenge=None):
    msg = ""
    if challenge is not None:
        msg += "Unknown challenge: {}\n\n".format(args.challenge)

    msg += "Available challenges:\n  "
    msg += "\n  ".join(_get_available_challenges())
    msg += "\nwhere {N} is an integer."
    print(msg)
    sys.exit(1)

def parse_args():
    general_parser = argparse.ArgumentParser(add_help=False)

    general_group = general_parser.add_argument_group('General settings')
    general_group.add_argument("--output", default="./tw_games/", metavar="PATH",
                               help="Path where to save the generated game.")
    general_group.add_argument('--seed', type=int, default=0)
    general_group.add_argument('--nb_games', type=int, default=2000)

    general_group.add_argument("--view", action="store_true",
                               help="Display the resulting game.")
    general_group.add_argument("-v", "--verbose", action="store_true")
    general_group.add_argument("-f", "--force", action="store_true")

    cfg_group = general_parser.add_argument_group('Grammar settings')
    cfg_group.add_argument("--theme", default="house",
                           help="Theme to use for generating the text. Default: %(default)s")
    cfg_group.add_argument("--include-adj", action="store_true",
                           help="Turn on adjectives.")
    cfg_group.add_argument("--blend-descriptions", action="store_true",
                           help="Blend descriptions across consecutive sentences.")
    cfg_group.add_argument("--ambiguous-instructions", action="store_true",
                           help="Refer to an object using its type (e.g. red container vs. red chest).")
    cfg_group.add_argument("--only-last-action", action="store_true",
                           help="Intruction only describes the last action of quest.")
    cfg_group.add_argument("--blend-instructions", action="store_true",
                           help="Blend instructions across consecutive actions.")

    parser = argparse.ArgumentParser(parents=[general_parser])
    subparsers = parser.add_subparsers(dest="subcommand", help='Kind of game to make.')

    custom_parser = subparsers.add_parser("custom", parents=[general_parser],
                                          help='Make a custom game.')
    custom_parser.add_argument("--world-size", type=int, default=10, metavar="SIZE",
                               help="Nb. of rooms in the world.")
    custom_parser.add_argument("--nb-objects", type=int, default=15, metavar="NB",
                               help="Nb. of objects in the world.")
    custom_parser.add_argument("--quest-length", type=int, default=10, metavar="LENGTH",
                               help="Minimum nb. of actions the quest requires to be completed.")
    custom_parser.add_argument("--quest-breadth", type=int, default=3, metavar="BREADTH",
                               help="Control how non-linear a quest can be.")

    challenge_parser = subparsers.add_parser("challenge", parents=[general_parser],
                                             help='Generate a game for one of the challenges.')
    challenge_parser.add_argument("challenge",
                                  help="Name of the builtin challenges, e.g. `tw-coin_collector-level210`")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    options = textworld.GameOptions()
    options.grammar.theme = args.theme
    options.grammar.include_adj = args.include_adj
    options.grammar.only_last_action = args.only_last_action
    options.grammar.blend_instructions = args.blend_instructions
    options.grammar.blend_descriptions = args.blend_descriptions
    options.grammar.ambiguous_instructions = args.ambiguous_instructions

    if args.subcommand == "custom":
        print("generating randomly generated games")
        world_sizes = list(range(3, args.world_size))
        nb_objects_list = list(range(8, args.nb_objects))
        quest_lengths = list(range(5, args.quest_length))

        print("Making %d games in %s" % (args.nb_games, args.output))
        for i in tqdm(range(args.seed, args.seed + args.nb_games + 1)):
            options.nb_rooms = random.choice(world_sizes)
            options.nb_objects = random.choice(nb_objects_list)
            options.quest_length = random.choice(quest_lengths)
            options.seeds = i
            game_file, game = textworld.make(options, args.output)
    elif args.subcommand == "challenge":
        try:
            _, challenge, level = args.challenge.split("-")
        except:
            exit_listing_challenges()

        if challenge not in textworld.challenges.CHALLENGES:
            exit_listing_challenges(args.challenge)

        level = int(level.lstrip("level"))
        make_game = textworld.challenges.CHALLENGES[challenge]

        for i in tqdm(range(args.seed, args.seed + args.nb_games + 1)):
            options.seeds = i
            game = make_game(level, options)
            game_file = textworld.generator.compile_game(game, args.output, force_recompile=args.force)