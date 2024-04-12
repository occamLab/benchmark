import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt

FB_DATA_DIR = Path(__file__).parent.parent / "data/.cache/firebase_data"
IMG_ZERO = (
    FB_DATA_DIR
    / "testing_2E4723D2-57C7-4AA1-B3B3-CE276ABF0DC7_ayush_mar_3_rotated/ace/test/rgb/00579.color.jpg"
)
IMG_ONE = (
    FB_DATA_DIR
    / "testing_7AAC6056-FEA5-4712-8134-26B13499316C_ayush_mar_3_rotated/ace/test/rgb/00319.color.jpg"
)
IMGS_DIR = Path(__file__).parent / "imgs"


def rgb2ii(img, alpha):
    """Convert RGB image to illumination invariant image."""
    ii_image = (
        0.5
        + np.log(img[:, :, 1] / float(255))
        - alpha * np.log(img[:, :, 2] / float(255))
        - (1 - alpha) * np.log(img[:, :, 0] / float(255))
    )

    return ii_image


def main():
    img_zero = Image.open(IMG_ZERO)
    img_one = Image.open(IMG_ONE)

    img_zero.save(IMGS_DIR / "night.jpg")
    img_one.save(IMGS_DIR / "day.jpg")

    img_zero_ii = rgb2ii(np.array(img_zero), 0.333)
    img_one_ii = rgb2ii(np.array(img_one), 0.333)

    plt.imsave(str(IMGS_DIR / "night_ii.jpg"), img_zero_ii, cmap='gray')
    # plt.imsave(str(IMGS_DIR / "night_ii.jpg"), img_zero_ii)
    # plt.savefig(str(IMGS_DIR / "night_ii.jpg"))

    # cv2.imwrite(str(IMGS_DIR / "night_ii.jpg"), img_zero_ii)
    # cv2.waitKey()
    # cv2.imwrite(str(IMGS_DIR / "day_ii.jpg"), img_one_ii)
    # cv2.waitKey()
    # img_zero = cv2.imread(str(IMG_ZERO))
    # img_one = cv2.imread(str(IMG_ONE))

    # cv2.imwrite(str(IMGS_DIR / "night.jpg"), img_zero)
    # cv2.imwrite(str(IMGS_DIR / "day.jpg"), img_one)

    # img_zero_ii = rgb2ii(cv2.cvtColor(img_zero, cv2.COLOR_BGR2RGB), 0.333)
    # img_one_ii = rgb2ii(cv2.cvtColor(img_one, cv2.COLOR_BGR2RGB), 0.333)

    # cv2.imwrite(str(IMGS_DIR / "night_ii.jpg"), img_zero_ii)
    # cv2.imwrite(str(IMGS_DIR / "day_ii.jpg"), img_one_ii)
    # breakpoint()

    # img_zero_recon = cv2.cvtColor(img_zero_ii, cv2.COLOR_GRAY2RGB)
    # img_one_recon = cv2.cvtColor(img_one_ii, cv2.COLOR_GRAY2RGB)

    # cv2.imwrite(str(IMGS_DIR / "night_recon.jpg"), img_zero_recon)
    # cv2.imwrite(str(IMGS_DIR / "day_recon.jpg"), img_one_recon)


if __name__ == "__main__":
    main()
