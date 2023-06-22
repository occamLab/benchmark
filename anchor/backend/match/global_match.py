from pathlib import Path
import argparse
from hloc import extract_features, match_features, match_dense
from hloc import pairs_from_covisibility, pairs_from_retrieval

import anchor.backend.data.firebase

"""
    Given two sets of videos, find relevant feature matchings in the image frames. 
    The process follows these stages: 
        1) In the first stage we feed the image sequences into NetVLAD to create global image descriptors. Then for 
            every frame in the localization video, we find the most similar frames from the mapping video. 
        2) The image pairs of similar localization frame : mapping frame are fed through a local feature detector 
            such as LoFTR to find image correspondence. 
"""


def featurepoint_extraction(input_images: Path, output_path: Path, num_pair: int):
    image_pairs = output_path / f'pairs-query-netvlad.txt'  # top-k retrieved by NetVLAD

    # Setup the extraction/matching configurations
    retrieval_conf = extract_features.confs['netvlad']
    matcher_conf = match_dense.confs['loftr']

    # Run global descriptor extraction
    global_descriptors = extract_features.main(retrieval_conf, input_images, output_path, overwrite=True)

    # Retrieve image pairs
    pairs_from_retrieval.main(global_descriptors, image_pairs, num_pair, query_prefix='localization-video', db_model=None)

    # Run matches against retrieved image pairs
    features, loc_matches = match_dense.main(matcher_conf, image_pairs, input_images, export_dir=output_path, overwrite=True)


# test the matchings here
if __name__ == '__main__':
    tar_firebase_path: str = "iosLoggerDemo/DQP1QbWk6WVZOFN6OpZiQXsfpsB3"
    tar_file_name: str = "27FB2D9E-5898-4DC9-97AB-7D08F231E649.tar"

    downloader = anchor.backend.data.firebase.FirebaseDownloader()
    extracted_location: Path = downloader.extract_ios_logger_tar(tar_firebase_path, tar_file_name)
    featurepoint_extraction(extracted_location, extracted_location, 2)

