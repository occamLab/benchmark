from pathlib import Path
from pprint import pformat
import argparse

from hloc import extract_features, match_features, match_dense
from hloc import pairs_from_covisibility, pairs_from_retrieval


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
matcher_conf = match_dense.confs['loftr_aachen']

# Run global descriptor extraction
global_descriptors = extract_features.main(retrieval_conf, images, args.outputs, overwrite=True)

# Retrieve image pairs
pairs_from_retrieval.main(
    global_descriptors, loc_pairs, args.num_loc,
    query_prefix='query', db_model=None)

# Run matches against retrieved image pairs
features, loc_matches = match_dense.main(matcher_conf, loc_pairs, images, export_dir=args.outputs, overwrite=True)

