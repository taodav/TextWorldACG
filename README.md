# TextWorldACG
Scripts for generating the TextWorldACG dataset (https://arxiv.org/abs/1812.00855)

The script `sample_games.py` will generate games into the folder specified in the `parse_args` function.

(For the ACG dataset as per the workshop paper, include the argument `--subcommand custom``).

To parse the games generated using the above script, run the script `dataset/acg.py` specifying the folder which you
generated games (as the `games_dir` argument).

Currently these scripts do not support tokenization. This repository is not being actively maintained.

