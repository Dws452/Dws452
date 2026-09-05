import os
import random
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFilter

USERNAME = "Dws452"
OUTPUT = "cat.gif"
CELL, GAP = 14, 4
COLS, ROWS = 53, 7
LEFT, TOP, BOTTOM = 42, 34, 22

BG = (13, 17, 23)
LEVELS = [
    (22, 27, 34),
    (14, 68, 41),
    (25, 115, 59),
    (48, 163, 84),
    (87, 211, 100),
]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount }
        }
      }
    }
  }
}
"""

CAT = [
    "   ##      ",
    "  ####     ",
    " #E###     ",
    " #######T  ",
    "  #######  ",
    " #  ##  #  ",
    "#   ##   # ",
]
CAT2 = [
    "   ##      ",
    "  ####     ",
    " #E###     ",
    " ####### T ",
    "  #######  ",
    "#   ##   # ",
    "  # ## #   ",
]

def get_data():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN не найден")
    r = requests.post(
        "https://api.github.com/graphql",
        json={"query": QUERY, "variables": {"login": USERNAME}},
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]

def build_grid(calendar):
    grid = [[0] * ROWS for _ in range(COLS)]
    weeks = calendar["weeks"][-COLS:]
    for x, week in enumerate(weeks):
        for day in week["contributionDays"]:
            d = datetime.strptime(day["date"], "%Y-%m-%d")
            y = (d.weekday() + 1) % 7  # Sunday = 0
            grid[x][y] = day["contributionCount"]
    return grid

def get_level(value, maximum):
    if value == 0:
        return 0
    ratio = value / max(1, maximum)
    return 1 if ratio <= .25 else 2 if ratio <= .5 else 3 if ratio <= .75 else 4

def path():
    result = []
    for y in range(ROWS):
        xs = range(COLS) if y % 2 == 0 else range(COLS - 1, -1, -1)
        for x in xs:
            result.append((x, y))
    return result

def draw_cat(image, x, y, frame_no, left=False):
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((x-8, y-8, x+30, y+25), fill=(255, 205, 60, 130))
    glow = glow.filter(ImageFilter.GaussianBlur(8))
    image.paste(glow, (0, 0), glow)

    draw = ImageDraw.Draw(image)
    sprite = CAT2 if frame_no % 2 else CAT
    if left:
        sprite = [row[::-1] for row in sprite]

    scale = 2
    colors = {"#": (255, 204, 92), "E": (30, 35, 40), "T": (255, 175, 65)}
    for sy, row in enumerate(sprite):
        for sx, ch in enumerate(row):
            if ch in colors:
                px, py = x + sx * scale, y + sy * scale
                draw.rectangle((px, py, px+scale-1, py+scale-1), fill=colors[ch])
    draw.point((x + 2*scale + 1, y + 2*scale), fill=(255,255,255))

def make_frame(grid, pos, n, maximum, sparks):
    width = LEFT*2 + COLS*(CELL+GAP)
    height = TOP + ROWS*(CELL+GAP) + BOTTOM
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)

    draw.text((LEFT, 9), f"{USERNAME}  •  Pixel Cat", fill=(180,190,200))

    for x in range(COLS):
        for y in range(ROWS):
            color = LEVELS[get_level(grid[x][y], maximum)]
            px, py = LEFT+x*(CELL+GAP), TOP+y*(CELL+GAP)
            draw.rounded_rectangle((px,py,px+CELL,py+CELL), radius=3, fill=color)

    # Sparkles behind the cat
    for sx, sy, life in sparks:
        if life > 0:
            draw.line((sx-2,sy,sx+2,sy), fill=(255,220,100), width=1)
            draw.line((sx,sy-2,sx,sy+2), fill=(255,220,100), width=1)

    gx, gy = pos
    cx = LEFT + gx*(CELL+GAP) - 3
    cy = TOP + gy*(CELL+GAP) - 3
    draw_cat(image, cx, cy, n, left=(gy % 2 == 1))
    return image

def main():
    print("🐱 Pixel Cat for", USERNAME)
    calendar = get_data()
    grid = build_grid(calendar)
    maximum = max(max(row) for row in grid) if grid else 1

    frames, sparks = [], []
    route = path()

    for n, (x, y) in enumerate(route):
        # Spawn sparkle when cat crosses a non-empty cell.
        if grid[x][y] > 0 and random.random() < .65:
            sparks.append((
                LEFT+x*(CELL+GAP)+CELL//2,
                TOP+y*(CELL+GAP)+CELL//2,
                8,
            ))

        sparks = [(sx, sy, life-1) for sx,sy,life in sparks if life > 1]
        frame = make_frame(grid, (x,y), n, maximum, sparks)
        frames.extend([frame, frame.copy()])

    frames[0].save(
        OUTPUT, save_all=True, append_images=frames[1:],
        duration=45, loop=0, optimize=True, disposal=2
    )
    print("✅ Created", OUTPUT)

if __name__ == "__main__":
    main()
