from PIL import Image, ImageDraw, ImageOps
import math
from pathlib import Path


SCALE = 4
W, H = 120, 96
FRAMES = 30
RABBIT_X_BASE = 30
GROUND_Y = 72
RABBIT_SOURCE_IMAGE = Path(
    r"C:\Users\tripa\.cursor\projects\c-Users-tripa-android\assets\c__Users_tripa_AppData_Roaming_Cursor_User_workspaceStorage_fdf23d18b2ade8cf2d7e1512bf1071b3_images_Screenshot__442_-58163ec7-2b01-4abb-b073-c7061a560870.png"
)


def rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


PALETTE = {
    "sky1": rgb("#9EDBFF"),
    "sky2": rgb("#AEE5FF"),
    "sky3": rgb("#C1EEFF"),
    "leaf1": rgb("#16884C"),
    "leaf2": rgb("#1FA65B"),
    "leaf3": rgb("#41BE73"),
    "leaf4": rgb("#74D994"),
    "trunk": rgb("#B86E3E"),
    "trunk_dark": rgb("#8F4F2E"),
    "ground1": rgb("#59D64A"),
    "ground2": rgb("#3FBE42"),
    "ground3": rgb("#2FA33C"),
    "water": rgb("#3FB5F2"),
    "water2": rgb("#2898D9"),
    "white": rgb("#FFFFFF"),
    "black": rgb("#111111"),
    "outline": rgb("#1A1732"),
    "rabbit": rgb("#D69778"),
    "rabbit2": rgb("#BE775F"),
    "rabbit_light": rgb("#E9B49A"),
    "pink": rgb("#EB7FA1"),
    "carrot": rgb("#F77F2F"),
    "carrot_dark": rgb("#DF6420"),
    "carrot_leaf": rgb("#3AAE57"),
    "mush_red": rgb("#DF4564"),
    "mush_cap": rgb("#F5EBDD"),
    "flower": rgb("#F2F9FF"),
}


def draw_pixel_rect(draw, x, y, w, h, color):
    draw.rectangle((x * SCALE, y * SCALE, (x + w) * SCALE - 1, (y + h) * SCALE - 1), fill=color)


def build_rabbit_sprite():
    if RABBIT_SOURCE_IMAGE.exists():
        src = Image.open(RABBIT_SOURCE_IMAGE).convert("RGBA")
        # Crop the rabbit artwork panel from the provided screenshot.
        crop = src.crop((450, 150, 720, 430))
        small = crop.resize((44, 44), Image.Resampling.NEAREST)

        # Remove the light beige panel background by color-keying near the corner.
        bg = small.getpixel((2, 2))
        px = small.load()
        for y in range(small.height):
            for x in range(small.width):
                r, g, b, a = px[x, y]
                if abs(r - bg[0]) < 20 and abs(g - bg[1]) < 20 and abs(b - bg[2]) < 20:
                    px[x, y] = (r, g, b, 0)

        # Remove thin white baseline artifact near feet from screenshot source.
        foot_cutoff = int(small.height * 0.72)
        for y in range(foot_cutoff, small.height):
            for x in range(small.width):
                r, g, b, a = px[x, y]
                if a > 0 and r > 228 and g > 228 and b > 228:
                    px[x, y] = (r, g, b, 0)

        # Trim extra transparent area and scale for crisp pixel display.
        box = small.getbbox()
        if box:
            small = small.crop(box)
        # Use the provided rabbit image only and make it face right.
        small = ImageOps.mirror(small)
        return small.resize((36 * SCALE, 36 * SCALE), Image.Resampling.NEAREST)
    else:
        # Create a simple test rabbit sprite
        sprite = Image.new("RGBA", (36 * SCALE, 36 * SCALE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(sprite)
        # Simple rabbit silhouette
        draw.ellipse((6 * SCALE, 16 * SCALE, 20 * SCALE, 28 * SCALE), fill=PALETTE["rabbit"])  # body
        draw.ellipse((14 * SCALE, 8 * SCALE, 22 * SCALE, 18 * SCALE), fill=PALETTE["rabbit"])  # head
        draw.rectangle((16 * SCALE, 2 * SCALE, 18 * SCALE, 10 * SCALE), fill=PALETTE["rabbit2"])  # left ear
        draw.rectangle((22 * SCALE, 2 * SCALE, 24 * SCALE, 10 * SCALE), fill=PALETTE["rabbit2"])  # right ear
        draw.ellipse((16 * SCALE, 12 * SCALE, 18 * SCALE, 14 * SCALE), fill=PALETTE["black"])  # eye
        return sprite


def draw_background(draw, t):
    sky_cycle = [PALETTE["sky1"], PALETTE["sky2"], PALETTE["sky3"]]
    sky = sky_cycle[(t // 8) % len(sky_cycle)]
    draw_pixel_rect(draw, 0, 0, W, H, sky)

    # Distant tree wall (parallax layer 1)
    offset_far = (t * 1) % 28
    for i in range(-2, 8):
        tx = i * 22 - offset_far
        draw_pixel_rect(draw, tx + 9, 26, 4, 21, PALETTE["trunk"])
        draw_pixel_rect(draw, tx + 10, 26, 1, 21, PALETTE["trunk_dark"])
        draw_pixel_rect(draw, tx, 17, 22, 10, PALETTE["leaf1"])
        draw_pixel_rect(draw, tx + 2, 14, 18, 5, PALETTE["leaf2"])
        draw_pixel_rect(draw, tx + 4, 12, 14, 3, PALETTE["leaf3"])

    # Foreground trees (parallax layer 2)
    offset_mid = (t * 2) % 40
    for i in range(-1, 5):
        tx = i * 34 - offset_mid
        draw_pixel_rect(draw, tx + 12, 34, 5, 24, PALETTE["trunk"])
        draw_pixel_rect(draw, tx + 14, 34, 1, 24, PALETTE["trunk_dark"])
        draw_pixel_rect(draw, tx + 2, 24, 25, 12, PALETTE["leaf2"])
        draw_pixel_rect(draw, tx + 5, 20, 20, 5, PALETTE["leaf3"])
        draw_pixel_rect(draw, tx + 8, 18, 14, 3, PALETTE["leaf4"])

    # Mid bushes
    offset_bush = (t * 3) % 22
    for i in range(-1, 8):
        bx = i * 18 - offset_bush
        draw_pixel_rect(draw, bx, 57, 14, 6, PALETTE["leaf2"])
        draw_pixel_rect(draw, bx + 2, 55, 10, 3, PALETTE["leaf3"])
        draw_pixel_rect(draw, bx + 4, 54, 6, 2, PALETTE["leaf4"])

    # River strip with highlights
    draw_pixel_rect(draw, 0, 64, W, 8, PALETTE["water"])
    draw_pixel_rect(draw, 0, 70, W, 2, PALETTE["water2"])
    for i in range(0, W, 10):
        if (i + t) % 20 < 10:
            draw_pixel_rect(draw, i, 66, 5, 1, PALETTE["white"])
        if (i + t * 2) % 24 < 6:
            draw_pixel_rect(draw, i + 2, 68, 2, 1, PALETTE["sky2"])

    # Lilies / tiny flowers over water
    for i in range(0, W, 24):
        lx = (i + (t * 2)) % W
        draw_pixel_rect(draw, lx, 65, 3, 1, PALETTE["leaf4"])
        draw_pixel_rect(draw, lx + 1, 64, 1, 1, PALETTE["flower"])

    # Ground and details
    draw_pixel_rect(draw, 0, 72, W, 24, PALETTE["ground1"])
    draw_pixel_rect(draw, 0, 84, W, 12, PALETTE["ground2"])
    for i in range(0, W, 7):
        if (i + t) % 14 < 7:
            draw_pixel_rect(draw, i, 79, 3, 2, PALETTE["ground3"])

    # Mushrooms and flowers like reference forest
    for i in range(10, W, 28):
        x = (i - t * 2) % (W + 12) - 6
        draw_pixel_rect(draw, x + 2, 70, 2, 3, PALETTE["mush_cap"])
        draw_pixel_rect(draw, x + 1, 69, 4, 2, PALETTE["mush_red"])
        draw_pixel_rect(draw, x + 2, 69, 1, 1, PALETTE["mush_cap"])
        draw_pixel_rect(draw, x + 4, 69, 1, 1, PALETTE["mush_cap"])
    for i in range(5, W, 16):
        fx = (i + t) % W
        draw_pixel_rect(draw, fx, 74, 1, 2, PALETTE["leaf3"])
        draw_pixel_rect(draw, fx - 1, 73, 3, 1, PALETTE["flower"])


def draw_rabbit(draw, x, y, t):
    ear_bob = 1 if (t % 6) < 3 else 0
    paw_shift = 1 if (t % 8) < 4 else 0
    leg_pose = (t % 10) < 5

    # Body / head masses
    draw_pixel_rect(draw, x + 9, y + 11, 14, 9, PALETTE["rabbit"])
    draw_pixel_rect(draw, x + 11, y + 16, 11, 4, PALETTE["rabbit2"])
    draw_pixel_rect(draw, x + 17, y + 4, 11, 9, PALETTE["rabbit"])
    draw_pixel_rect(draw, x + 20, y + 8, 6, 4, PALETTE["rabbit2"])
    draw_pixel_rect(draw, x + 18, y + 11, 5, 4, PALETTE["rabbit_light"])

    # Ears with pink inner detail
    draw_pixel_rect(draw, x + 22, y - 8 - ear_bob, 4, 13, PALETTE["rabbit2"])
    draw_pixel_rect(draw, x + 23, y - 4 - ear_bob, 2, 7, PALETTE["pink"])
    draw_pixel_rect(draw, x + 27, y - 5 - ear_bob, 4, 11, PALETTE["rabbit2"])
    draw_pixel_rect(draw, x + 28, y - 2 - ear_bob, 2, 6, PALETTE["pink"])

    # Tail, belly and eye
    draw_pixel_rect(draw, x + 6, y + 13, 4, 4, PALETTE["white"])
    draw_pixel_rect(draw, x + 16, y + 14, 6, 4, PALETTE["white"])
    draw_pixel_rect(draw, x + 24, y + 7, 1, 1, PALETTE["black"])

    # Carrot in paws
    draw_pixel_rect(draw, x + 12, y + 11 + paw_shift, 4, 6, PALETTE["carrot"])
    draw_pixel_rect(draw, x + 13, y + 12 + paw_shift, 2, 4, PALETTE["carrot_dark"])
    draw_pixel_rect(draw, x + 10, y + 9 + paw_shift, 5, 3, PALETTE["carrot_leaf"])
    draw_pixel_rect(draw, x + 18, y + 13 + paw_shift, 2, 3, PALETTE["white"])

    # Legs alternate pose
    if leg_pose:
        draw_pixel_rect(draw, x + 11, y + 20, 5, 2, PALETTE["rabbit2"])
        draw_pixel_rect(draw, x + 19, y + 19, 5, 2, PALETTE["rabbit2"])
    else:
        draw_pixel_rect(draw, x + 10, y + 19, 5, 2, PALETTE["rabbit2"])
        draw_pixel_rect(draw, x + 20, y + 20, 5, 2, PALETTE["rabbit2"])

    # Outline for crisp pixel character style
    outline_parts = [
        (8, 11, 1, 9), (9, 10, 14, 1), (23, 11, 1, 9), (9, 20, 14, 1),
        (16, 4, 1, 9), (17, 3, 11, 1), (28, 4, 1, 9), (17, 13, 11, 1),
        (22, -8 - ear_bob, 1, 13), (25, -8 - ear_bob, 1, 13),
        (27, -5 - ear_bob, 1, 11), (30, -5 - ear_bob, 1, 11),
    ]
    for ox, oy, ow, oh in outline_parts:
        draw_pixel_rect(draw, x + ox, y + oy, ow, oh, PALETTE["outline"])


def make_frame(t):
    img = Image.new("RGB", (W * SCALE, H * SCALE), PALETTE["sky1"])
    draw = ImageDraw.Draw(img)
    draw_background(draw, t)

    # Smooth jump arc + slight forward motion loop
    cycle = (2 * math.pi * t) / FRAMES
    jump_cycle = (2 * math.pi * 3 * t) / FRAMES
    jump = int(12 * max(0, math.sin(jump_cycle)))
    travel_progress = t / (FRAMES - 1)
    rabbit_w_units = RABBIT_SPRITE.width // SCALE
    x_start = -rabbit_w_units + 2
    x_end = W - 2
    x = int(x_start + (x_end - x_start) * travel_progress) + int(1 * math.sin(cycle * 2))
    y = GROUND_Y - 24 - jump
    img.paste(RABBIT_SPRITE, (x * SCALE, (y - 8) * SCALE), RABBIT_SPRITE)
    return img


def main():
    frames = [make_frame(i) for i in range(FRAMES)]
    out_path = "rabbit_forest_loop.gif"
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        optimize=False,
        duration=85,
        loop=0,
        disposal=2,
    )
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    RABBIT_SPRITE = build_rabbit_sprite()
    main()
