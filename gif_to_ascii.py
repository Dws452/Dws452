from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ==========================================
# НАСТРОЙКИ
# ==========================================

# Название твоей GIF
INPUT_FILE = "tenor.gif"

# Название готовой ASCII-анимации
OUTPUT_FILE = "ascii.gif"

# Ширина ASCII
WIDTH = 125

# Символы от тёмного к светлому
ASCII_CHARS = " .:-=+*#%@"

# Коррекция высоты символов
CHAR_ASPECT = 0.45

# Размер шрифта
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
# КАДР GIF → ASCII
# ==========================================

def frame_to_ascii(frame):

    # Переводим изображение в оттенки серого
    gray = frame.convert("L")

    original_width, original_height = gray.size

    # Сохраняем пропорции
    aspect_ratio = original_height / original_width

    height = int(
        WIDTH * aspect_ratio * CHAR_ASPECT
    )

    height = max(1, height)

    # Изменяем размер
    gray = gray.resize(
        (WIDTH, height),
        Image.Resampling.LANCZOS
    )

    pixels = np.array(gray)

    # Яркость → ASCII-символ
    indices = (
        pixels / 255 *
        (len(ASCII_CHARS) - 1)
    ).astype(int)

    lines = []

    for row in indices:

        line = "".join(
            ASCII_CHARS[index]
            for index in row
        )

        lines.append(line)

    return lines


# ==========================================
# ASCII → КАРТИНКА
# ==========================================

def create_ascii_frame(lines):

    # Размер одного символа
    char_width = 8
    char_height = 14

    width = WIDTH * char_width
    height = len(lines) * char_height

    # Чёрный фон
    image = Image.new(
        "RGB",
        (width, height),
        (0, 0, 0)
    )

    draw = ImageDraw.Draw(image)

    # Рисуем ASCII
    for y, line in enumerate(lines):

        draw.text(
            (0, y * char_height),
            line,
            font=FONT,
            fill=(255, 255, 255)
        )

    return image


# ==========================================
# ОТКРЫВАЕМ ТВОЮ GIF
# ==========================================

print("🎞️ Открываю:", INPUT_FILE)

gif = Image.open(INPUT_FILE)

print("🎬 Количество кадров:", gif.n_frames)

# Скорость оригинальной GIF
duration = gif.info.get("duration", 100)

frames = []


# ==========================================
# ОБРАБОТКА ВСЕХ КАДРОВ
# ==========================================

for frame_number in range(gif.n_frames):

    print(
        f"⚙️ Обрабатываю кадр "
        f"{frame_number + 1}/{gif.n_frames}"
    )

    gif.seek(frame_number)

    frame = gif.convert("RGB")

    ascii_lines = frame_to_ascii(frame)

    ascii_frame = create_ascii_frame(
        ascii_lines
    )

    frames.append(ascii_frame)


# ==========================================
# СОХРАНЯЕМ ASCII GIF
# ==========================================

if not frames:
    raise RuntimeError(
        "Не удалось создать кадры!"
    )

print("💾 Сохраняю ASCII-анимацию...")

frames[0].save(
    OUTPUT_FILE,
    save_all=True,
    append_images=frames[1:],
    duration=duration,
    loop=0,
    optimize=False
)

print()
print("================================")
print("✅ ГОТОВО!")
print("================================")
print("Исходная GIF:", INPUT_FILE)
print("Результат:", OUTPUT_FILE)
print("Кадров:", len(frames))
print("================================")
