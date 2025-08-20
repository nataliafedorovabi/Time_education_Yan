from io import BytesIO
import math
import random
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont


def _pick_bright_color() -> Tuple[int, int, int]:
    palette = [
        (255, 231, 150),  # warm yellow
        (176, 232, 255),  # sky blue
        (200, 255, 200),  # mint
        (255, 200, 220),  # pink
        (255, 220, 180),  # peach
        (210, 210, 255),  # lilac
    ]
    return random.choice(palette)


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        # If user adds a TTF named DejaVuSans.ttf next to the script, we try it
        return ImageFont.truetype("DejaVuSans.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def _draw_centered_text(draw: ImageDraw.ImageDraw, text: str, center: Tuple[int, int], font: ImageFont.ImageFont, fill=(0, 0, 0)) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((center[0] - w // 2, center[1] - h // 2), text, font=font, fill=fill)


def render_time_of_day_card(label: str, size: Tuple[int, int] = (800, 600)) -> bytes:
    bg = _pick_bright_color()
    image = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(image)

    # Simple symbolic illustration
    cx, cy = size[0] // 2, size[1] // 2
    big_font = _load_font(64)
    small_font = _load_font(36)

    # Decorative circle and icon-like shape
    radius = min(size) // 5
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(0, 0, 0), width=6)

    if label == "утро":
        draw.arc((cx - radius, cy - radius, cx + radius, cy + radius), start=200, end=340, fill=(255, 200, 0), width=12)
        _draw_centered_text(draw, "СОЛНЦЕ", (cx, cy + radius + 40), small_font, fill=(120, 90, 0))
    elif label == "день":
        draw.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=(255, 215, 0))
        _draw_centered_text(draw, "ЯРКО", (cx, cy + radius + 40), small_font, fill=(120, 90, 0))
    elif label == "вечер":
        draw.rectangle((cx - radius, cy - 10, cx + radius, cy + 10), fill=(255, 120, 0))
        _draw_centered_text(draw, "ТЕПЛО", (cx, cy + radius + 40), small_font, fill=(120, 60, 0))
    else:  # ночь
        draw.rectangle((cx - radius, cy - radius, cx + radius, cy + radius), outline=(40, 40, 80), width=6)
        draw.ellipse((cx - 15, cy - 15, cx + 15, cy + 15), fill=(200, 200, 255))
        _draw_centered_text(draw, "ТИХО", (cx, cy + radius + 40), small_font, fill=(30, 30, 90))

    _draw_centered_text(draw, label.upper(), (cx, int(size[1] * 0.18)), big_font)

    buf = BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


def render_text_card(text: str, size: Tuple[int, int] = (800, 600)) -> bytes:
    bg = _pick_bright_color()
    image = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(image)
    title_font = _load_font(56)
    body_font = _load_font(48)

    parts = text.split("\n", 1)
    title = parts[0]
    body = parts[1] if len(parts) > 1 else ""

    _draw_centered_text(draw, title, (size[0] // 2, int(size[1] * 0.25)), title_font)
    _draw_centered_text(draw, body, (size[0] // 2, int(size[1] * 0.55)), body_font)

    buf = BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


def render_clock(hour: int, minute: int, size: Tuple[int, int] = (800, 800)) -> bytes:
    image = Image.new("RGB", size, (250, 250, 255))
    draw = ImageDraw.Draw(image)
    center = (size[0] // 2, size[1] // 2)
    radius = int(min(size) * 0.4)

    # Face
    draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), outline=(0, 0, 0), width=8, fill=(255, 255, 255))

    # Hour marks
    mark_font = _load_font(36)
    for h in range(1, 13):
        angle = (h % 12) * (2 * math.pi / 12) - math.pi / 2
        tx = int(center[0] + math.cos(angle) * (radius - 40))
        ty = int(center[1] + math.sin(angle) * (radius - 40))
        _draw_centered_text(draw, str(h), (tx, ty), mark_font)

    # Hands
    minute_angle = (minute / 60.0) * 2 * math.pi - math.pi / 2
    hour_angle = ((hour % 12) / 12.0 + (minute / 60.0) / 12.0) * 2 * math.pi - math.pi / 2

    minute_length = int(radius * 0.85)
    hour_length = int(radius * 0.6)

    mx = int(center[0] + math.cos(minute_angle) * minute_length)
    my = int(center[1] + math.sin(minute_angle) * minute_length)
    hx = int(center[0] + math.cos(hour_angle) * hour_length)
    hy = int(center[1] + math.sin(hour_angle) * hour_length)

    draw.line((center[0], center[1], mx, my), fill=(50, 50, 50), width=8)
    draw.line((center[0], center[1], hx, hy), fill=(0, 0, 0), width=12)
    draw.ellipse((center[0] - 8, center[1] - 8, center[0] + 8, center[1] + 8), fill=(0, 0, 0))

    # Caption
    caption_font = _load_font(48)
    _draw_centered_text(draw, f"{hour}:{minute:02d}", (center[0], int(size[1] * 0.9)), caption_font, fill=(20, 20, 20))

    buf = BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()
