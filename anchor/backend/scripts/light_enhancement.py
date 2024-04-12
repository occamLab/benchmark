import numpy as np  # array manipulation

# from huggingface_hub import from_pretrained_keras  # download the model
# import keras  # deep learning
from PIL import Image  # Image processing
from pathlib import Path
import os
import shutil
from tensorflow.python.ops.numpy_ops import np_config
from copy import deepcopy

np_config.enable_numpy_behavior()


FB_DATA_DIR = Path(__file__).parent.parent / "data/.cache/firebase_data"

combined_model_name = (
    "training_ua-7c140933b99a14568ee768781fb5c9b2_ayush_mar_4_5_combined"
)
individual_model_names = [
    "training_ua-7c140933b99a14568ee768781fb5c9b2_ayush_mar_4",
    "training_ua-1bab71c5f9279e0777539be4abd6ae2b_ayush_mar_5",
]
all_models = individual_model_names + [combined_model_name]
test_datasets = [
    # 9:30
    "testing_FE49EDB3-4A95-4B60-A942-5E41463DAEEF_ayush_mar_3",
    # 12:00
    "testing_7AAC6056-FEA5-4712-8134-26B13499316C_ayush_mar_3",
    # Days later
    "testing_2E4723D2-57C7-4AA1-B3B3-CE276ABF0DC7_ayush_mar_3",
]


def convert_image(img_path: Path, model):
    low_light_img = Image.open(img_path).convert("RGB")
    image = keras.preprocessing.image.img_to_array(low_light_img)
    image = image.astype("float32") / 255.0
    image = np.expand_dims(image, axis=0)
    output = model(image)
    output_image = output[0] * 255.0
    output_image = output_image.clip(0, 255)
    output_image = output_image.reshape(
        (np.shape(output_image)[0], np.shape(output_image)[1], 3)
    )
    output_image = np.uint32(output_image)
    img = Image.fromarray(output_image.astype("uint8"), "RGB")
    img.save(img_path)


def main():
    model = from_pretrained_keras("keras-io/lowlight-enhance-mirnet", compile=False)
    total_models = len(test_datasets + all_models)
    model_counter = 1
    for dir_name in test_datasets + all_models:
        test_dir = FB_DATA_DIR / dir_name
        enhanced_dir = FB_DATA_DIR / f"{dir_name}_enhanced"
        if enhanced_dir.exists():
            shutil.rmtree(enhanced_dir)
        shutil.copytree(test_dir, enhanced_dir)

        img_dir = enhanced_dir / "extracted/localization-video"

        img_files = [x for x in os.walk(img_dir)][0][2]
        num_files = len(img_files)
        counter = 1
        for img_file_name in [x for x in os.walk(img_dir)][0][2]:
            img_path = img_dir / img_file_name
            convert_image(img_path, model)
            print(
                f"{model_counter}/{total_models} models, {counter}/{num_files} test imgs converted"
            )
            counter += 1

        if dir_name.startswith("training"):
            img_dir = enhanced_dir / "extracted/mapping-video"

            img_files = [x for x in os.walk(img_dir)][0][2]
            num_files = len(img_files)
            counter = 1
            for img_file_name in [x for x in os.walk(img_dir)][0][2]:
                img_path = img_dir / img_file_name
                convert_image(img_path, model)
                print(
                    f"{model_counter}/{total_models} models, {counter}/{num_files} train imgs converted"
                )
                counter += 1

        model_counter += 1


def main2():
    count = 1
    for dir_name in [combined_model_name] + individual_model_names:
        localization_video = (
            FB_DATA_DIR / f"{dir_name}_enhanced/extracted/localization-video"
        )
        rgb_dir = FB_DATA_DIR / f"{dir_name}_enhanced/ace/test/rgb"

        for enhanced_img_name in [x for x in os.walk(localization_video)][0][2]:
            enhanced_img_path = localization_video / enhanced_img_name
            frame_num = enhanced_img_name.split(".")[0]
            rgb_img_path = rgb_dir / f"{int(frame_num):05}.color.jpg"
            shutil.copyfile(enhanced_img_path, rgb_img_path)
            print(count)
            count += 1

        mapping_video = FB_DATA_DIR / f"{dir_name}_enhanced/extracted/mapping-video"
        rgb_dir = FB_DATA_DIR / f"{dir_name}_enhanced/ace/train/rgb"

        for enhanced_img_name in [x for x in os.walk(mapping_video)][0][2]:
            enhanced_img_path = mapping_video / enhanced_img_name
            frame_num = enhanced_img_name.split(".")[0]
            rgb_img_path = rgb_dir / f"{int(frame_num):05}.color.jpg"
            shutil.copyfile(enhanced_img_path, rgb_img_path)
            print(count)
            count += 1


def rotate_image():
    rot = -np.pi / 2
    pose_transform = np.array(
        [
            [np.cos(rot), -np.sin(rot), 0, 0],
            [np.sin(rot), np.cos(rot), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )
    num_models = len(test_datasets + all_models)
    model_counter = 0
    for dir_name in test_datasets + all_models:
        data_dir = FB_DATA_DIR / dir_name
        rot_dir = FB_DATA_DIR / f"{dir_name}_rotated"
        if rot_dir.exists():
            shutil.rmtree(rot_dir)
        shutil.copytree(data_dir, rot_dir)

        test_dir = rot_dir / "ace/test"
        num_images = len([x for x in os.walk(test_dir / "rgb")][0][2])
        img_counter = 0
        model_counter += 1
        for img_name in [x for x in os.walk(test_dir / "rgb")][0][2]:
            img_counter += 1
            print(
                f"{model_counter}/{num_models} models {img_counter}/{num_images} images"
            )
            img_num = img_name.split(".")[0]
            img_path = test_dir / "rgb" / img_name
            pose_path = test_dir / "poses" / f"{img_num}.pose.txt"
            calibration_path = test_dir / "calibration" / f"{img_num}.calibration.txt"

            original_image = Image.open(img_path)
            if original_image.size[0] > original_image.size[1]:
                rotated_image = original_image.transpose(Image.ROTATE_270)
                rotated_image.save(img_path)

                with open(pose_path, "r") as pose_file:
                    data = pose_file.readlines()
                    data = np.array(
                        [[float(num) for num in d.strip("\n").split(" ")] for d in data]
                    )
                new_pose = data @ pose_transform
                with open(pose_path, "w") as pose_file:
                    pose_file.write(
                        f"{new_pose[0,0]} {new_pose[0,1]} {new_pose[0,2]} {new_pose[0,3]}\n"
                        + f"{new_pose[1,0]} {new_pose[1,1]} {new_pose[1,2]} {new_pose[1,3]}\n"
                        + f"{new_pose[2,0]} {new_pose[2,1]} {new_pose[2,2]} {new_pose[2,3]}\n"
                        + f"{new_pose[3,0]} {new_pose[3,1]} {new_pose[3,2]} {new_pose[3,3]}"
                    )

                with open(calibration_path, "r") as cal_file:
                    data = cal_file.readlines()
                    data = np.array(
                        [[float(num) for num in d.strip("\n").split(" ")] for d in data]
                    )
                new_intrinsics = deepcopy(data)
                new_intrinsics[0, 0] = data[1, 1]
                new_intrinsics[1, 1] = data[0, 0]
                new_intrinsics[0, 2] = rotated_image.size[0] - data[1, 2]
                new_intrinsics[1, 2] = data[0, 2]
                with open(calibration_path, "w") as cal_file:
                    cal_file.write(
                        f"{new_intrinsics[0,0]} {new_intrinsics[0,1]} {new_intrinsics[0,2]}\n"
                        + f"{new_intrinsics[1,0]} {new_intrinsics[1,1]} {new_intrinsics[1,2]}\n"
                        + f"{new_intrinsics[2,0]} {new_intrinsics[2,1]} {new_intrinsics[2,2]}\n"
                    )

        if "training" in dir_name:
            train_dir = rot_dir / "ace/train"
            for img_name in [x for x in os.walk(train_dir / "rgb")][0][2]:
                img_num = img_name.split(".")[0]
                img_path = train_dir / "rgb" / img_name
                pose_path = train_dir / "poses" / f"{img_num}.pose.txt"
                calibration_path = (
                    train_dir / "calibration" / f"{img_num}.calibration.txt"
                )

                original_image = Image.open(img_path)
                if original_image.size[0] > original_image.size[1]:
                    rotated_image = original_image.transpose(Image.ROTATE_270)
                    rotated_image.save(img_path)

                    with open(pose_path, "r") as pose_file:
                        data = pose_file.readlines()
                        data = np.array(
                            [
                                [float(num) for num in d.strip("\n").split(" ")]
                                for d in data
                            ]
                        )
                    new_pose = data @ pose_transform
                    with open(pose_path, "w") as pose_file:
                        pose_file.write(
                            f"{new_pose[0,0]} {new_pose[0,1]} {new_pose[0,2]} {new_pose[0,3]}\n"
                            + f"{new_pose[1,0]} {new_pose[1,1]} {new_pose[1,2]} {new_pose[1,3]}\n"
                            + f"{new_pose[2,0]} {new_pose[2,1]} {new_pose[2,2]} {new_pose[2,3]}\n"
                            + f"{new_pose[3,0]} {new_pose[3,1]} {new_pose[3,2]} {new_pose[3,3]}"
                        )

                    with open(calibration_path, "r") as cal_file:
                        data = cal_file.readlines()
                        data = np.array(
                            [
                                [float(num) for num in d.strip("\n").split(" ")]
                                for d in data
                            ]
                        )
                    new_intrinsics = deepcopy(data)
                    new_intrinsics[0, 0] = data[1, 1]
                    new_intrinsics[1, 1] = data[0, 0]
                    new_intrinsics[0, 2] = rotated_image.size[0] - data[1, 2]
                    new_intrinsics[1, 2] = data[0, 2]
                    with open(calibration_path, "w") as cal_file:
                        cal_file.write(
                            f"{new_intrinsics[0,0]} {new_intrinsics[0,1]} {new_intrinsics[0,2]}\n"
                            + f"{new_intrinsics[1,0]} {new_intrinsics[1,1]} {new_intrinsics[1,2]}\n"
                            + f"{new_intrinsics[2,0]} {new_intrinsics[2,1]} {new_intrinsics[2,2]}\n"
                        )


if __name__ == "__main__":
    # main()
    # main2()
    rotate_image()
