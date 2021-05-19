"""
Combine the dataframes.
"""
from ..config import config_rand
from ..functions import combine_PS_rand_outputs



def main(config, seeds):
    combine_PS_rand_outputs(config, seeds)


if __name__=="__main__":
    seeds = list(range(31))
    main(config_rand, seeds)