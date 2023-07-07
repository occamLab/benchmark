from pathlib import Path
import numpy as np


class Extracted:

    def __init__(self, extract_root: Path):
        self.sensors_extracted = {
            "mapping_phase": {
                "intrinsics": [],
                "poses": [],
                "april_tags": [],
                "video": [],
            },
            "localization_phase": {
                "intrinsics": [],
                "poses": [],
                "april_tags": [],
                "video": [],
            }
        }
        self.extract_root = extract_root

    @staticmethod
    def get_phase_key(mapping_phase: bool):
        return "mapping_phase" if mapping_phase else "localization_phase"

    # append a video timestamp to the extracted data
    def append_video_timestamp(self, timestamp: int, frame_path: Path, frame_num: int, mapping_phase: bool):
        phase = Extracted.get_phase_key(mapping_phase)
        self.sensors_extracted[phase]["video"].append({"timestamp": timestamp, "frame_path": frame_path, "frame_num": frame_num})

    def append_intrinsics_data(self, timestamp: int, fx: float, fy: float, cx: float, cy: float, mapping_phase: bool):
        phase = Extracted.get_phase_key(mapping_phase)
        intrinsics = {"timestamp": timestamp, "fx": fx, "fy": fy, "cx": cx, "cy": cy}
        self.sensors_extracted[phase]["intrinsics"].append(intrinsics)

    # append a timestamp with pose data
    def append_pose_data(self, pose_object: any, mapping_phase: bool):
        phase = Extracted.get_phase_key(mapping_phase)
        self.sensors_extracted[phase]["poses"].append(pose_object)

    # append april tag detection
    def append_april_tag(self, timestamp: float, rotation_matrix: [float], mapping_phase: bool):
        phase = Extracted.get_phase_key(mapping_phase)
        april_tag_object = {"timestamp": timestamp, "rotation_matrix": rotation_matrix}
        print(april_tag_object)
        self.sensors_extracted[phase]["april_tags"].append(april_tag_object)

    def match_given_sensor(self, phase: str, match_against: str):
        """
            The timestamps that we can get out of the video frames are not entirely accurate. Firstly: the timestamps
            are encoded based on an arbitrary integer scale known as PTS (presentation timestamp). This means that there
            will be floating point errors in the timestamps that we read.

            Secondly, the video encoder on the IOS side may drop frames (and this does frequently happen in practice)

            As a result, we need to perform matching on the timestamps to figure out the correspondence between
            video timestamps and other sensor data timestamps
        """

        # frames can be re-arranged, so I'm not if the extraction order of the frames is necessarily
        # the same as their PTS (presentation) order.
        self.sensors_extracted[phase]["video"].sort(key=lambda x: x["timestamp"])

        # just to be safe, let's sort the sensor we are matching against as well
        self.sensors_extracted[phase][match_against].sort(key=lambda x: x["timestamp"])

        frame_idx = 0
        sensor_idx = 0
        match_count = 0

        while frame_idx < len(self.sensors_extracted[phase]["video"]) and sensor_idx < len(
                self.sensors_extracted[phase][match_against]):
            frame_timestamp = self.sensors_extracted[phase]["video"][frame_idx]["timestamp"]
            sensor_timestamp = self.sensors_extracted[phase][match_against][sensor_idx]["timestamp"]

            # ArFrames feed at roughly 30fps, so we can filter with a 1ms cutoff window to match frames
            if abs(frame_timestamp - sensor_timestamp) < 0.001:
                self.sensors_extracted[phase]["video"][frame_idx][match_against] \
                    = self.sensors_extracted[phase][match_against][sensor_idx]
                sensor_idx += 1
                frame_idx += 1
                match_count += 1
            elif frame_timestamp > sensor_timestamp:
                sensor_idx += 1
            else:
                frame_idx += 1

        print(
            f'[INFO]: Matched {match_count} video frames out of {len(self.sensors_extracted[phase]["video"])} total frames in {phase} with {match_against}')
        assert match_count == len(
            self.sensors_extracted[phase]["video"]), "failed to match all video frames to sensor data"

    def match_all_sensor(self):
        for phase in self.sensors_extracted:
            for sensor in self.sensors_extracted[phase]:
                if sensor not in ["video", "april_tags"]:
                    self.match_given_sensor(phase, sensor)

    def transform_poses_in_global_frame(self):
        """
            We are not using april tags for now so this function is disabled
        """
        return
        for phase in self.sensors_extracted:
            # todo: perform some kind of averaging for the rotation angle of the april tag to get a more accurate measurement of its position
            true_april_tag_loc = np.reshape(self.sensors_extracted[phase]["april_tags"][0]["rotation_matrix"], (4, 4)).transpose()

            # average the translations on the april tag to get a better reading
            average_pose_translation = np.zeros([4, 1], dtype=float)
            for april_tag in self.sensors_extracted[phase]["april_tags"]:
                april_tag_loc = np.reshape(april_tag["rotation_matrix"], (4, 4)).transpose()
                average_pose_translation = np.add(average_pose_translation, april_tag_loc[:, [3]])
            average_pose_translation /= len(self.sensors_extracted[phase]["april_tags"])
            print(average_pose_translation, true_april_tag_loc)
            true_april_tag_loc[:, [3]] = average_pose_translation
            print(true_april_tag_loc)

           # exit(0)

            # transform pose data relative to april tag location
            for idx, pose in enumerate(self.sensors_extracted[phase]["poses"]):
                pose_transform = np.reshape(pose["rotation_matrix"], (4, 4)).transpose()
                relative_to_april = np.matmul(np.linalg.inv(true_april_tag_loc), pose_transform)
                original_list_form = relative_to_april.transpose().flatten().tolist()
                self.sensors_extracted[phase]["poses"][idx]["rotation_matrix"] = original_list_form

