from pathlib import Path
from pprint import pformat
import argparse

from hloc import extract_features, match_features
from hloc import pairs_from_covisibility, pairs_from_retrieval
from hloc import colmap_from_nvm, triangulation, localize_sfm


parser = argparse.ArgumentParser()
parser.add_argument('--dataset', type=Path, default='datasets/arkit',
                    help='Path to the dataset, default: %(default)s')
parser.add_argument('--outputs', type=Path, default='outputs/arkit',
                    help='Path to the output directory, default: %(default)s')
parser.add_argument('--num_loc', type=int, default=2,
                    help='Number of image pairs for loc, default: %(default)s')
args = parser.parse_args()

# Setup the paths
images = args.dataset / 'images/'

# Setup the outputs
loc_pairs = args.outputs / f'pairs-query-netvlad.txt'  # top-k retrieved by NetVLAD

# Setup the extraction/matching configurations
retrieval_conf = extract_features.confs['netvlad']

# Run global descriptor extraction
global_descriptors = extract_features.main(retrieval_conf, images, args.outputs)

# Retrieve image pairs
pairs_from_retrieval.main(
    global_descriptors, loc_pairs, args.num_loc,
    query_prefix='query', db_model=None)
