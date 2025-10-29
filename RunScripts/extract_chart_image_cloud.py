import fitz, io, base64
from PIL import Image

RAW_BOXES = [
    {"page": 0, "rect": fitz.Rect(0, 55, 1225, 375), "label": "Daily Planner", "scale": 1.56},
    {"page": 1, "rect": fitz.Rect(40, 0, 550, 500), "label": "Winds & Temp", "scale": 1.0},
    {"page": 1, "rect": fitz.Rect(40, 500, 550, 750), "label": "2 Hr Precip", "scale": 1.0},
    {"page": 2, "rect": fitz.Rect(40, 0, 550, 250), "label": "Accumulated Precip", "scale": 1.0},
]
MERGE_ORDER = ["Winds & Temp", "Daily Planner", ["2 Hr Precip", "Accumulated Precip"]]
FINAL_SCALE = 0.256

def _clamp(rect, w, h):
    return fitz.Rect(max(0, rect.x0), max(0, rect.y0), min(w, rect.x1), min(h, rect.y1))

def _stack_vert(images):
    width = max(im.width for im in images)
    height = sum(im.height for im in images)
    out = Image.new("RGB", (width, height), (255, 255, 255))
    y = 0
    for im in images:
        out.paste(im, (0, y))
        y += im.height
    return out

def run(pdf_path: str) -> dict:
    doc = fitz.open(pdf_path)
    zoom = 300 / 72
    mat = fitz.Matrix(zoom, zoom)
    parts = {}

    for box in RAW_BOXES:
        page = doc[box["page"]]
        r = _clamp(box["rect"], page.rect.width, page.rect.height)
        pix = page.get_pixmap(matrix=mat, clip=r)
        from io import BytesIO
        img = Image.open(BytesIO(pix.tobytes("png")))
        if box["scale"] != 1.0:
            img = img.resize((int(img.width*box["scale"]), int(img.height*box["scale"])), Image.LANCZOS)
        parts[box["label"]] = img

    cols = []
    for item in MERGE_ORDER:
        if isinstance(item, list):
            cols.append(_stack_vert([parts[k] for k in item]))
        else:
            cols.append(parts[item])

    total_w = sum(i.width for i in cols)
    max_h = max(i.height for i in cols)
    merged = Image.new("RGB", (total_w, max_h), (255, 255, 255))
    x = 0
    for im in cols:
        merged.paste(im, (x, 0))
        x += im.width

    if FINAL_SCALE != 1.0:
        merged = merged.resize((int(merged.width*FINAL_SCALE), int(merged.height*FINAL_SCALE)), Image.LANCZOS)

    buf = io.BytesIO()
    merged.save(buf, format="PNG")
    return {"png_b64": base64.b64encode(buf.getvalue()).decode("ascii")}
