from pathlib import Path
import json
from utils.error import compute_rotational_error, compute_translation_error
from utils.data_models import TestInfo, MapTestInfo
import matplotlib.pyplot as plt

DATASET_INFO_PATH = Path(__file__).parent / "utils/dataset.json"
DATASET_NAME = "ayush_mar_1"


def main():
    with open(DATASET_INFO_PATH, "r") as file:
        json_data = json.load(file)

    if DATASET_NAME not in json_data:
        raise KeyError(f"Invalid map Name: {DATASET_NAME}")

    map_data = json_data[DATASET_NAME]
    map_data["tests"] = [TestInfo(data=None, **test) for test in map_data["tests"]]
    test_info = MapTestInfo(name=DATASET_NAME, **map_data)
    test_info.load_all_data()
    data = test_info.tests[0].data
    fig = plt.figure()
    data.plot_data(fig)
    plt.show()


if __name__ == "__main__":
    main()
