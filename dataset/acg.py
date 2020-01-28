import os
import json
import textworld
from tqdm import tqdm

from agents.walkthrough import WalkthroughAgent, WalkthroughDone
from utils.files import get_games_list
from utils.parse import get_state_entities, parse_game_state


class TextWorldACG:
    def __init__(self, games_dir='../tw_games/',
                 file_name='../data/train.text.dataset.json',
                 save_data=True):
        """

        :param games_dir: directory for all the generated games
        """
        super(TextWorldACG, self).__init__()
        self.games_dir = games_dir
        self.file_name = file_name

        self.save_data = save_data

        self.state_action_pairs = []
        self.state_mappings = {}
        self.counter = 0

        if os.path.isfile(self.file_name):
            with open(self.file_name) as f:
                self.state_action_pairs = json.load(f)
        else:
            self.parse_all_games(self.games_dir)

            if self.save_data:
                with open(self.file_name, 'w') as outfile:
                    json.dump(self.state_action_pairs, outfile)

    def __getitem__(self, idx):
        return self.state_action_pairs[idx]

    def __len__(self):
        return len(self.state_action_pairs)

    def parse_all_games(self, games_dir):
        """
        Walks through and parses all in given directory (self.games_dir)
        """

        print("Parsing all games into state/action pairs")
        ulx_files = get_games_list(games_dir)

        agent = WalkthroughAgent()
        pbar = tqdm(ulx_files, total=len(ulx_files))
        for game in pbar:
            self.walk_game(game, agent)

    @classmethod
    def run_one_game(cls, game_file):
        env = textworld.start(game_file)
        env.activate_state_tracking()
        game_state = env.reset()

        return env, game_state

    def walk_game(self, game, agent):
        """
        walks through an entire game and returns its state/action pairs.
        :param game:
        :param agent:
        :return: array of state, action pairs (untokenized)
        """

        env = textworld.start(game)
        logic = env.game.kb.logic
        env.enable_extra_info("description")
        env.enable_extra_info("inventory")
        env.activate_state_tracking()
        game_state = env.reset()
        entities = [(ent.name.lower(), logic.inform7.types[ent.type].kind) for ent in env.game.infos.values() if ent.name]
        agent.reset(env)
        done = False
        reward = 0
        previous_actions = []
        is_first = True
        while not done:
            try:
                command = agent.act(game_state, reward, done)
                feedback = ''
                if not is_first:
                    feedback = game_state.feedback.replace('\n', ' ')
                else:
                    is_first = False

                state, inventory, actions = parse_game_state(game_state)
                state, feedback, inventory = state.lower(), feedback.lower(), inventory.lower()
                comb_state = state + inventory

                state_entities = get_state_entities(entities, comb_state)
                if state + inventory in self.state_mappings:
                    index = self.state_mappings[state + inventory]
                    state_copy, feedback_copy, inventory_copy, actions_copy, state_entities_copy, previous_actions_copy = self.state_action_pairs[index]

                    # we're here if the state descriptions are the same.
                    feedback_copy = feedback + feedback_copy
                    actions_copy = list(set(actions_copy + actions))
                    state_entities_copy = list(set(state_entities + state_entities_copy))
                    previous_actions_copy = list(set(previous_actions + previous_actions_copy))
                    self.state_action_pairs[index] = [state_copy, feedback_copy, inventory_copy, actions_copy, state_entities_copy, previous_actions_copy]
                else:
                    self.state_mappings[state + inventory] = self.counter
                    self.state_action_pairs.append([state, feedback, inventory, actions, state_entities, previous_actions[:]])
                    self.counter += 1

                game_state, reward, done = env.step(command)
                previous_actions.append(command)
            except WalkthroughDone:
                break

if __name__ == "__main__":
    dataset = TextWorldACG()

