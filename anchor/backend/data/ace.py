from anchor.backend.data.extracted import Extracted
from anchor.backend.data.firebase import FirebaseDownloader


def prepare_ace_data(extracted_data: Extracted):
    ace_input = extracted_data.extract_root / "ace"

    map_our_phases_to_theirs = {
        "mapping_phase": "train",
        "localization_phase": "test"
    }


    for phase in extracted_data.sensors_extracted:
        matched_data = extracted_data.sensors_extracted[phase]["video"]
        write_location = ace_input / map_our_phases_to_theirs[phase]
        write_location.mkdir(parents=True, exist_ok=True)

        for data in matched_data:

            pass




# test the extractor here
if __name__ == '__main__':
    downloader = FirebaseDownloader("iosLoggerDemo/Ljur5BYFXdhsGnAlEsmjqyNG5fJ2",
                                    "047F9850-20BB-4AC0-9650-C2558C9EFC03.tar")
    downloader.extract_ios_logger_tar()
    prepare_ace_data(downloader.extracted_data)

