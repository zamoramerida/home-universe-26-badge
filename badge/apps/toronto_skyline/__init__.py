"""A tiny day-to-night postcard of Toronto and the CN Tower."""

import os
import sys


APP_DIR = "/system/apps/toronto_skyline"
os.chdir(APP_DIR)
sys.path.insert(0, APP_DIR)

screen.font = font.nope

VIEWS = (
    {
        "name": "DAWN",
        "sky": (245, 157, 125),
        "glow": (255, 216, 145),
        "far": (104, 91, 112),
        "city": (40, 54, 77),
        "water": (47, 105, 132),
        "water_line": (124, 183, 190),
        "windows": (255, 207, 135),
        "star": None,
    },
    {
        "name": "DAY",
        "sky": (83, 171, 210),
        "glow": (255, 225, 146),
        "far": (113, 157, 170),
        "city": (43, 74, 91),
        "water": (35, 115, 153),
        "water_line": (129, 210, 216),
        "windows": (206, 225, 192),
        "star": None,
    },
    {
        "name": "NIGHT",
        "sky": (13, 24, 53),
        "glow": (255, 205, 124),
        "far": (35, 50, 79),
        "city": (20, 33, 56),
        "water": (14, 45, 80),
        "water_line": (58, 103, 142),
        "windows": (255, 192, 93),
        "star": (230, 238, 255),
    },
)

# x, width, height; the CN Tower is drawn separately in front.
BUILDINGS = (
    (0, 17, 22), (12, 13, 34), (27, 16, 25), (43, 14, 39),
    (57, 12, 29), (72, 13, 22), (85, 16, 31), (101, 12, 25),
    (113, 17, 37), (131, 13, 27), (144, 16, 33),
)

view_index = 0
postcard = True
tilt_reference = None
parallax_x = 0.0
parallax_y = 0.0


def draw_buildings(view, ground, tilt_x, tilt_y):
    width = screen.width
    far_x = int(round(tilt_x * 0.4 * width / 160))
    far_y = int(round(tilt_y * 0.3 * width / 160))
    near_x = int(round(tilt_x * 0.8 * width / 160))
    near_y = int(round(tilt_y * 0.6 * width / 160))

    screen.pen = color.rgb(*view["far"])
    for x, building_width, height in BUILDINGS:
        screen.rectangle(x * width // 160 + far_x, ground - height + far_y,
                         building_width * width // 160, height)

    screen.pen = color.rgb(*view["city"])
    for x, building_width, height in BUILDINGS:
        left = x * width // 160 + near_x
        scaled_width = building_width * width // 160
        top = ground - height + near_y
        screen.rectangle(left + 2, top + 3, max(2, scaled_width - 4), height - 3)

    screen.pen = color.rgb(*view["windows"])
    for x, building_width, height in BUILDINGS:
        left = x * width // 160 + near_x
        scaled_width = building_width * width // 160
        top = ground - height + near_y
        for row in range(2, max(3, height - 5), 7):
            for column in range(3, max(4, scaled_width - 3), 5):
                screen.rectangle(left + column, top + row, 2, 2)


def draw_cn_tower(view, ground):
    width = screen.width
    x = width * 83 // 160
    screen.pen = color.rgb(218, 227, 226)
    screen.rectangle(x - 1, ground - 42, 3, 42)
    screen.rectangle(x - 2, ground - 49, 5, 7)
    screen.rectangle(x - 5, ground - 51, 11, 2)
    screen.rectangle(x - 8, ground - 55, 17, 4)
    screen.rectangle(x - 4, ground - 57, 9, 2)
    screen.rectangle(x - 1, ground - 70, 3, 13)

    screen.pen = color.rgb(184, 197, 200)
    screen.rectangle(x - 12, ground - 2, 25, 2)

    # The beacon sits at the top of the antenna, above the observation deck.
    if (badge.ticks // 500) % 2 == 0:
        screen.pen = color.rgb(255, 77, 89)
        screen.rectangle(x, ground - 72, 2, 2)


def draw_sun_or_moon(view, tilt_x, tilt_y):
    width = screen.width
    x = width * 102 // 160 + int(round(tilt_x * 0.2 * width / 160))
    y = 31 + int(round(tilt_y * 0.2 * width / 160))
    screen.pen = color.rgb(*view["glow"])
    screen.circle(vec2(x, y), 7)
    if view["name"] == "NIGHT":
        screen.pen = color.rgb(*view["sky"])
        screen.circle(vec2(x + 4, y - 3), 6)

    if view["star"]:
        screen.pen = color.rgb(*view["star"])
        for sx, sy in ((18, 30), (39, 18), (61, 34), (112, 16), (143, 45)):
            screen.rectangle(sx * width // 160, sy, 2, 2)


def draw_water(view, ground, tilt_x, tilt_y):
    width = screen.width
    height = screen.height
    water_y = int(round(tilt_y * 1.2 * width / 160))
    screen.pen = color.rgb(*view["water"])
    screen.rectangle(0, ground + water_y, width, height - ground - water_y)

    screen.pen = color.rgb(*view["water_line"])
    for row in (ground + 5, ground + 11, ground + 18):
        y = min(row + water_y, height - 17)
        water_x = int(round(tilt_x * 1.2 * width / 160))
        for x in range((row * 3) % 13 + water_x, width, 23):
            screen.rectangle(x, y, 7 + (x % 8), 1)


def update_parallax():
    global tilt_reference, parallax_x, parallax_y

    ax, ay, az, _gx, _gy, _gz = badge.imu()
    magnitude = (ax * ax + ay * ay + az * az) ** 0.5

    if magnitude:
        normalized = (ax / magnitude, ay / magnitude)
        if tilt_reference is None:
            tilt_reference = normalized
        target_x = (normalized[0] - tilt_reference[0]) * 12
        target_y = (normalized[1] - tilt_reference[1]) * 12
        if badge.upside_down():
            target_x = -target_x
            target_y = -target_y
        target_x = max(-5, min(5, target_x))
        target_y = max(-5, min(5, target_y))
    else:
        target_x = 0
        target_y = 0

    blend = min(1, max(0, badge.ticks_delta) / 160)
    parallax_x += (target_x - parallax_x) * blend
    parallax_y += (target_y - parallax_y) * blend


def update():
    global view_index, postcard

    if badge.pressed(BUTTON_LEFT):
        view_index = (view_index - 1) % len(VIEWS)
    if badge.pressed(BUTTON_RIGHT):
        view_index = (view_index + 1) % len(VIEWS)
    if badge.pressed(BUTTON_SELECT):
        postcard = not postcard

    width = screen.width
    height = screen.height
    update_parallax()
    view = VIEWS[view_index]
    ground = height - 31

    screen.pen = color.rgb(*view["sky"])
    screen.rectangle(0, 0, width, height)
    draw_sun_or_moon(view, parallax_x, parallax_y)
    draw_buildings(view, ground, parallax_x, parallax_y)
    draw_cn_tower(view, ground)
    draw_water(view, ground, parallax_x, parallax_y)

    screen.pen = color.rgb(12, 22, 38)
    screen.rectangle(0, height - 18, width, 18)
    screen.pen = color.rgb(255, 244, 224)
    screen.text("TORONTO / " + view["name"], 4, 5)
    if postcard:
        screen.text("THE 6IX", 4, 17)

    screen.pen = color.rgb(255, 244, 224)
    screen.text("TILT L/R SKY SEL CARD", 4, height - 16)


run(update)
