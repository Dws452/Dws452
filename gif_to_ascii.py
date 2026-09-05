from PIL import Image, ImageDraw, ImageFont, ImageSequence
import numpy as np


# ==========================================
# НАСТРОЙКИ
# ==========================================

INPUT_FILE = "tenor.gif"
OUTPUT_FILE = "ascii.gif"

# Количество ASCII-символов по ширине
WIDTH = 100

# Символы от тёмного к светлому
ASCII_CHARS = " .:-=+*#%@"

# Исправление пропорций символов
# Подбираем так, чтобы изображение не растягивалось
CHAR_RATIO = 0.50

# Размер текста
FONT_SIZE = 12


# ==========================================
# ШРИФТ
# ==========================================

try:
    FONT = ImageFont.truetype(
        "DejaVuSansMono.ttf",
        FONT_SIZE
    )
except:
    FONT = ImageFont.load_default()


# ==========================================
# ASCII КАДР
# ==========================================

def convert_to_ascii(frame):

    # Переводим в RGB
    frame = frame.convert("RGB")

    original_width, original_height = frame.size

    # Сохраняем исходные пропорции
    aspect = original_height / original_width

    # Высота ASCII
    ascii_height = max(
        1,
        int(WIDTH * aspect * CHAR_RATIO)
    )

    # Изменяем размер
    frame = frame.resize(
        (WIDTH, ascii_height),
        Image.Resampling.LANCZOS
    )

    # В оттенки серого
    gray = frame.convert("L")

    pixels = np.asarray(gray)

    # Яркость → индекс символа
    indexes = (
        pixels / 255 *
        (len(ASCII_CHARS) - 1)
    ).astype(np.int32)

    lines = []

    for row in indexes:

        line = "".join(
            ASCII_CHARS[int(i)]
            for i in row
        )

        lines.append(line)

    return lines


# ==========================================
# ASCII → ИЗОБРАЖЕНИЕ
# ==========================================

def make_ascii_image(lines):

    # Фиксированный размер символа
    CHAR_WIDTH = 8
    CHAR_HEIGHT = 14

    image_width = WIDTH * CHAR_WIDTH
    image_height = len(lines) * CHAR_HEIGHT

    # ОДИНАКОВЫЙ размер у каждого кадра
    image = Image.new(
        "RGB",
        (image_width, image_height),
        (0, 0, 0)
    )

    draw = ImageDraw.Draw(image)

    # Рисуем каждую строку отдельно
    for y, line in enumerate(lines):

        draw.text(
            (
                0,
                y * CHAR_HEIGHT
            ),
            line,
            font=FONT,
            fill=(255, 255, 255)
        )

    return image


# ==========================================
# ОТКРЫВАЕМ GIF
# ==========================================

print("================================")
print("🎞️ GIF → ASCII")
print("================================")

gif = Image.open(INPUT_FILE)

print(f"📁 Файл: {INPUT_FILE}")
print(f"🎬 Кадров: {gif.n_frames}")


# ==========================================
# FPS / СКОРОСТЬ
# ==========================================

duration = gif.info.get(
    "duration",
    100
)

# Если GIF сообщает слишком маленькую
# задержку — ограничиваем её
duration = max(duration, 30)


# ==========================================
# ОБРАБОТКА
# ==========================================

frames = []

for number, frame in enumerate(
    ImageSequence.Iterator(gif)
):

    print(
        f"⚙️ Кадр "
        f"{number + 1}/{gif.n_frames}"
    )

    # Каждый кадр независимо преобразуем
    frame = frame.convert("RGB")

    ascii_lines = convert_to_ascii(
        frame
    )

    ascii_image = make_ascii_image(
        ascii_lines
    )

    frames.append(ascii_image)


# ==========================================
# ПРОВЕРКА
# ==========================================

if len(frames) == 0:

    raise RuntimeError(
        "❌ Не удалось получить кадры GIF!"
    )


# ==========================================
# СОХРАНЕНИЕ
# ==========================================

print()
print("💾 Создаю ascii.gif...")

frames[0].save(
    OUTPUT_FILE,
    save_all=True,
    append_images=frames[1:],
    duration=duration,
    loop=0,
    disposal=2,
    optimize=False
)


print()
print("================================")
print("✅ ГОТОВО!")
print("================================")
print(f"Исходник: {INPUT_FILE}")
print(f"Результат: {OUTPUT_FILE}")
print(f"Кадров: {len(frames)}")
print(f"Ширина ASCII: {WIDTH}")
print("================================")
