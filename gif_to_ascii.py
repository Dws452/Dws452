from PIL import Image, ImageDraw, ImageFont
import numpy as np


#НАСТРОЙКИ--
INPUT_FILE = "tenor.gif"
OUTPUT_FILE = "ascii.gif"

WIDTH = 150

ASCII_CHARS = "@%#*+=-:. "

#Размер символов--
FONT_SIZE = 10


#ПРЕОБРАЗОВАНИЕ КАДРА В ASCII--


def frame_to_ascii(frame):

    gray = frame.convert("L")


    aspect_ratio = gray.height / gray.width

    height = max(
        1,
        int(WIDTH * aspect_ratio * 0.5)
    )


    gray = gray.resize((WIDTH, height))

    pixels = np.array(gray)

    indices = (
        pixels / 255 * (len(ASCII_CHARS) - 1)
    ).astype(int)

    ascii_lines = []

    for row in indices:
        line = "".join(
            ASCII_CHARS[index]
            for index in row
        )

        ascii_lines.append(line)

    return ascii_lines



#СОЗДАНИЕ ASCII-КАДРА--


def create_ascii_image(lines):


    char_width = 7
    char_height = 10

    width = WIDTH * char_width
    height = len(lines) * char_height


    image = Image.new(
        "RGB",
        (width, height),
        "black"
    )

    draw = ImageDraw.Draw(image)


    font = ImageFont.load_default()

    for y, line in enumerate(lines):

        draw.text(
            (2, y * char_height),
            line,
            fill="white",
            font=font
        )

    return image


#ОСНОВНАЯ ПРОГРАММА--


def main():

    print("Открываю GIF:", INPUT_FILE)

    gif = Image.open(INPUT_FILE)

    frames = []

    duration = gif.info.get("duration", 100)

    print("Количество кадров:", gif.n_frames)


    for frame_number in range(gif.n_frames):

        print(
            f"Обрабатываю кадр "
            f"{frame_number + 1}/{gif.n_frames}"
        )

        gif.seek(frame_number)

        frame = gif.convert("RGB")

        ascii_lines = frame_to_ascii(frame)

        ascii_image = create_ascii_image(
            ascii_lines
        )

        frames.append(ascii_image)

    if not frames:
        print("Ошибка: кадров не найдено.")
        return


    print("Сохраняю:", OUTPUT_FILE)

    frames[0].save(
        OUTPUT_FILE,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0
    )

    print()
    print("================================")
    print("ГОТОВО!")
    print("Создан файл:", OUTPUT_FILE)
    print("================================")


if __name__ == "__main__":
    main()
