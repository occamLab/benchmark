from pathlib import Path



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
                if sensor != "video":
                    self.match_given_sensor(phase, sensor)


    def transform_poses_in_global_frame(self):
        for phase in self.sensors_extracted:
            pass