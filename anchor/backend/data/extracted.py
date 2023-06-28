

class Extracted:

    def __init__(self):
        self.sensors_extracted = {
            "mapping_phase": {
                "intrinsics": [],
                "poses": [],
                "video_timestamps": []
            },
            "localization_phase": {
                "intrinsics": [],
                "poses": [],
                "video_timestamps": [],
            }
        }

    @staticmethod
    def get_phase_key(mapping_phase: bool):
        return "mapping_phase" if mapping_phase else "localization_phase"

    # append a video timestamp to the extracted data
    def append_video_timestamp(self, timestamp: int, mapping_phase: bool):
        phase = Extracted.get_phase_key(mapping_phase)
        self.sensors_extracted[phase]["video_timestamps"].append(timestamp)

    def append_intrinsics_data(self, timestamp: int, fx: float, fy: float, cx: float, cy: float, mapping_phase: bool):
        phase = Extracted.get_phase_key(mapping_phase)
        intrinsics = {"timestamp": timestamp, "fx": fx, "fy": fy, "cx": cx, "cy": cy}
        self.sensors_extracted[phase]["intrinsics"].append(intrinsics)

    def append_pose_data(self, pose_object: any, mapping_phase: bool):
        phase = Extracted.get_phase_key(mapping_phase)
        self.sensors_extracted[phase]["poses"].append(pose_object)

