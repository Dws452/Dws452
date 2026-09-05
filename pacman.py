import os
import math
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter

USERNAME = "Dws452"
OUTPUT = "pacman.gif"

CELL = 14
GAP = 4
MARGIN_X = 35
MARGIN_Y = 35

BG = (13, 17, 23)
EMPTY = (22, 27, 34)

# Цвета клеток активности
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
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def get_contributions():
    token = os.environ.get("GITHUB_TOKEN")

    if not token:
        raise RuntimeError("GITHUB_TOKEN не найден!")

    response = requests.post(
        "https://api.github.com/graphql",
        json={
            "query": QUERY,
            "variables": {"login": USERNAME},
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise RuntimeError(data["errors"])

    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def get_level(count, maximum):
    if count == 0:
        return 0

    if maximum <= 1:
        return 4

    ratio = count / maximum

    if ratio <= 0.25:
        return 1
    elif ratio <= 0.5:
        return 2
    elif ratio <= 0.75:
        return 3

    return 4


def draw_pacman(draw, x, y, frame, direction):
    """
    Рисуем маленького пиксельного Pac-Man.
    """

    cx = x + CELL // 2
    cy = y + CELL // 2

    radius = CELL // 2 + 2

    # Анимация рта
    mouth = 18 if frame % 2 == 0 else 42

    if direction == "right":
        start = mouth
        end = 360 - mouth

    elif direction == "left":
        start = 180 + mouth
        end = 180 - mouth

    elif direction == "down":
        start = 90 + mouth
        end = 90 - mouth

    else:
        start = 270 + mouth
        end = 270 - mouth

    draw.pieslice(
        (
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
        ),
        start=start,
        end=end,
        fill=(255, 220, 40),
    )


def create_frame(grid, pacman_pos, frame_number):
    weeks = len(grid)
    width = MARGIN_X * 2 + weeks * (CELL + GAP)
    height = MARGIN_Y * 2 + 7 * (CELL + GAP)

    image = Image.new("RGB", (width, height), BG)

    # Слой свечения
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    # Рисуем contribution graph
    for x in range(weeks):
        for y in range(7):

            count = grid[x][y]

            level = get_level(
                count,
                max(max(column) for column in grid)
            )

            color = LEVELS[level]

            px = MARGIN_X + x * (CELL + GAP)
            py = MARGIN_Y + y * (CELL + GAP)

            ImageDraw.Draw(image).rounded_rectangle(
                (
                    px,
                    py,
                    px + CELL,
                    py + CELL,
                ),
                radius=3,
                fill=color,
            )

    # Позиция Pac-Man
    px_index, py_index = pacman_pos

    px = MARGIN_X + px_index * (CELL + GAP)
    py = MARGIN_Y + py_index * (CELL + GAP)

    # Неоновое свечение
    glow_draw.ellipse(
        (
            px - 8,
            py - 8,
            px + CELL + 8,
            py + CELL + 8,
        ),
        fill=(255, 220, 40, 180),
    )

    glow = glow.filter(ImageFilter.GaussianBlur(7))
    image = Image.alpha_composite(
        image.convert("RGBA"),
        glow
    ).convert("RGB")

    draw = ImageDraw.Draw(image)

    # Направление
    direction = "right"

    if frame_number > 0:
        old_x, old_y = pacman_positions[
            max(0, frame_number - 1)
        ]

        if px_index < old_x:
            direction = "left"
        elif px_index > old_x:
            direction = "right"
        elif py_index < old_y:
            direction = "up"
        elif py_index > old_y:
            direction = "down"

    draw_pacman(
        draw,
        px,
        py,
        frame_number,
        direction,
    )

    return image


def build_grid(calendar):
    weeks = calendar["weeks"]

    grid = []

    for week in weeks:
        column = [0] * 7

        for day in week["contributionDays"]:
            date = datetime.strptime(
                day["date"],
                "%Y-%m-%d"
            )

            # Python: Monday=0 ... Sunday=6
            weekday = date.weekday()

            column[weekday] = day["contributionCount"]

        grid.append(column)

    return grid


def build_path(grid):
    """
    Pac-Man проходит весь график,
    двигаясь по строкам туда-сюда.
    """

    weeks = len(grid)

    path = []

    for y in range(7):

        if y % 2 == 0:
            x_range = range(weeks)
        else:
            x_range = range(weeks - 1, -1, -1)

        for x in x_range:
            path.append((x, y))

    return path


def main():

    print("================================")
    print("👾 PAC-MAN CONTRIBUTION GRAPH")
    print("================================")

    calendar = get_contributions()

    print(
        "Всего contributions:",
        calendar["totalContributions"]
    )

    grid = build_grid(calendar)

    global pacman_positions
    pacman_positions = build_path(grid)

    print("Клеток:", len(pacman_positions))

    frames = []

    # Делаем несколько кадров на одну позицию,
    # чтобы движение было плавнее
    for i, position in enumerate(pacman_positions):

        print(
            f"\rСоздание кадра {i + 1}/{len(pacman_positions)}",
            end=""
        )

        frame = create_frame(
            grid,
            position,
            i
        )

        # Каждый кадр повторяем 2 раза
        frames.append(frame)
        frames.append(frame.copy())

    print()
    print("💾 Сохраняю GIF...")

    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=45,
        loop=0,
        optimize=True,
    )

    print("================================")
    print("✅ ГОТОВО!")
    print("================================")
    print("Файл:", OUTPUT)


if __name__ == "__main__":
    main()
