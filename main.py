from PIL import Image
import math
import os
from os.path import isfile, join


def get_images(assets_path: str):
    files = []
    for f in os.listdir(assets_path):
        join_path = join(assets_path, f)
        if isfile(join_path):
            files.append(join_path)
    return files


IPHONE_8_COLS = 4
IPHONE_8_ROWS = 6

x_start, y_start = 54, 60
icon_size = 120
gap_x = 54
gap_y = 56


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

    return rgb_to_hsv(r, g, b)


def extract_icons_from_images(images: list[Image.Image]) -> list[dict]:
    icons = []

    for img in images:
        for row in range(IPHONE_8_ROWS):
            for col in range(IPHONE_8_COLS):
                x1 = x_start + col * (icon_size + gap_x)
                y1 = y_start + row * (icon_size + gap_y)

                x2 = x1 + icon_size
                y2 = y1 + icon_size

                icon = img.crop((x1, y1, x2, y2))

                hsv = get_hsv_from_image(icon)
                if sum(hsv) == 0:
                    continue
                icons.append({"icon": icon, "hsv": hsv})

    return icons


def create_sorted_icons_image(icons: list[Image.Image]) -> Image.Image:
    n_rows = math.ceil(len(icons) / IPHONE_8_COLS)

    new_img_width = IPHONE_8_COLS * (icon_size + gap_x) - gap_x
    new_img_height = n_rows * (icon_size + gap_y) - gap_y
    new_img = Image.new("RGB", (new_img_width, new_img_height), "black")

    for i, icon_data in enumerate(icons):
        row = i // IPHONE_8_COLS
        col = i % IPHONE_8_COLS
        x = col * (icon_size + gap_x)
        y = row * (icon_size + gap_y)
        new_img.paste(icon_data["icon"], (x, y))

    return new_img


def main():
    images = [Image.open(f) for f in get_images("./assets")]
    icons = extract_icons_from_images(images)
    icons.sort(key=lambda x: x["hsv"])

    new_img = create_sorted_icons_image(icons)
    new_img.show()


if __name__ == "__main__":
    main()
