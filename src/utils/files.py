import os

def get_games_list(games_dir='./gen_games/'):
    ulx_files = []
    for file in os.listdir(games_dir):
        # if file.startswith("tw-game") and file.endswith(".ulx"):
        if file.endswith(".ulx"):
            ulx_files.append(games_dir + file)
    return ulx_files