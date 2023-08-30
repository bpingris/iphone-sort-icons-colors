from PIL import Image
import math
from sklearn.cluster import KMeans
import numpy as np
import os
from os.path import isfile, join
from dataclasses import dataclass


@dataclass
class Gap:
    x: int
    y: int


@dataclass
class IPhoneConfig:
    cols: int
    rows: int
    gap: Gap
    icon_size: int
    x_start: int
    y_start: int


IPHONE_CONFIG = {
    "8": IPhoneConfig(
        cols=4, rows=6, gap=Gap(x=54, y=56), icon_size=120, x_start=54, y_start=60
    ),
}


def get_images(assets_path: str):
    files = []
    for f in os.listdir(assets_path):
        join_path = join(assets_path, f)
        if isfile(join_path):
            files.append(join_path)
    return files


def rgb_to_hsv(r, g, b) -> tuple:
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    diff = max_val - min_val
    if max_val == min_val:
        h = 0
    elif max_val == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_val == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    elif max_val == b:
        h = (60 * ((r - g) / diff) + 240) % 360
    if max_val == 0:
        s = 0
    else:
        s = (diff / max_val) * 100
    v = max_val * 100
    return h, s, v


def weighted_avg(hist: list) -> float:
    return sum(val * i for i, val in enumerate(hist)) / sum(hist)


def get_hsv_from_image(img: Image.Image) -> tuple:
    histogram = img.histogram()

    r_hist = histogram[0:256]
    g_hist = histogram[256 : 256 * 2]
    b_hist = histogram[256 * 2 : 256 * 3]

    r = weighted_avg(r_hist)
    g = weighted_avg(g_hist)
    b = weighted_avg(b_hist)

    return rgb_to_hsv(r, g, b), (r, g, b)


def extract_icons_from_images(
    images: list[Image.Image], config: IPhoneConfig
) -> list[dict]:
    icons = []
    feature_list = []

    for img in images:
        for row in range(config.rows):
            for col in range(config.cols):
                x1 = config.x_start + col * (config.icon_size + config.gap.x)
                y1 = config.y_start + row * (config.icon_size + config.gap.y)

                x2 = x1 + config.icon_size
                y2 = y1 + config.icon_size

                icon = img.crop((x1, y1, x2, y2))

                hsv, rgb = get_hsv_from_image(icon)
                if sum(hsv) == 0:
                    continue

                feature_list.append(rgb)
                icons.append({"icon": icon, "hsv": hsv})

    # Perform KMeans clustering
    feature_array = np.array(feature_list)
    kmeans = KMeans(n_clusters=7).fit(
        feature_array
    )  # You can change the number of clusters
    labels = kmeans.labels_

    for i, label in enumerate(labels):
        icons[i]["label"] = label
    return icons


def create_sorted_icons_image(
    icons: list[Image.Image], config: IPhoneConfig
) -> Image.Image:
    n_rows = math.ceil(len(icons) / config.cols)

    new_img_width = config.cols * (config.icon_size + config.gap.x) - config.gap.x
    new_img_height = n_rows * (config.icon_size + config.gap.y) - config.gap.y
    new_img = Image.new("RGB", (new_img_width, new_img_height), "black")

    for i, icon_data in enumerate(icons):
        row = i // config.cols
        col = i % config.cols
        x = col * (config.icon_size + config.gap.x)
        y = row * (config.icon_size + config.gap.y)
        new_img.paste(icon_data["icon"], (x, y))

    return new_img


def main():
    config = IPHONE_CONFIG["8"]

    images = [Image.open(f) for f in get_images("./assets")]
    icons = extract_icons_from_images(images, config)
    icons.sort(key=lambda x: x["label"])

    new_img = create_sorted_icons_image(icons, config)
    # new_img.save("post-sklearn.png")
    new_img.show()


if __name__ == "__main__":
    main()
