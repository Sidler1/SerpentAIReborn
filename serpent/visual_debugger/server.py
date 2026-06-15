"""Web visual debugger — a FastAPI replacement for the old Kivy app.

Renders the newest frame of each pipeline bucket as a PNG, on an
auto-refreshing page viewable in any browser. Run with ``serpent visual-debugger``
(or ``serpent.visual_debugger.server.run()``). Use the ``redis`` transport so the
producer (the running game agent) and this viewer share buckets across processes.
"""

from __future__ import annotations

import io

import numpy as np
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from PIL import Image

from serpent.visual_debugger.visual_debugger import VisualDebugger


def to_png_bytes(image_data: np.ndarray) -> bytes:
    array = image_data

    if array.dtype == bool:
        array = array.astype("uint8") * 255
    elif np.issubdtype(array.dtype, np.floating):
        array = np.clip(array * 255.0, 0, 255).astype("uint8")
    elif array.dtype != np.uint8:
        array = np.clip(array, 0, 255).astype("uint8")
    elif array.size and array.max() <= 1:
        array = array * 255

    image = Image.fromarray(array)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _placeholder_png() -> bytes:
    return to_png_bytes(np.zeros((64, 64, 3), dtype="uint8"))


_PAGE = """<!doctype html>
<html><head><title>Serpent.AI Visual Debugger</title>
<style>
  body {{ background:#23313f; color:#eee; font-family:sans-serif; margin:1rem; }}
  .grid {{ display:flex; flex-wrap:wrap; gap:1rem; }}
  .bucket {{ background:#1b2630; padding:.5rem; border-radius:6px; }}
  .bucket h3 {{ margin:.2rem; font-size:.9rem; font-weight:normal; color:#7fb; }}
  img {{ image-rendering:pixelated; max-width:480px; display:block; }}
</style></head>
<body>
  <h2>Serpent.AI Visual Debugger</h2>
  <div class="grid">{cards}</div>
  <script>
    setInterval(() => {{
      for (const img of document.querySelectorAll("img")) {{
        const base = img.src.split("?")[0];
        img.src = base + "?t=" + Date.now();
      }}
    }}, {interval_ms});
  </script>
</body></html>"""


def create_app(buckets=None) -> FastAPI:
    app = FastAPI(title="Serpent.AI Visual Debugger")
    debugger = VisualDebugger(buckets=buckets, clear=False)

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        cards = "".join(
            f'<div class="bucket"><h3>{bucket}</h3>'
            f'<img src="/bucket/{bucket}.png" alt="{bucket}"></div>'
            for bucket in debugger.available_buckets
        )
        return _PAGE.format(cards=cards, interval_ms=500)

    @app.get("/bucket/{bucket}.png")
    def bucket_image(bucket: str) -> Response:
        image_data = (
            debugger.peek_image_data(bucket) if bucket in debugger.available_buckets else None
        )
        png = _placeholder_png() if image_data is None else to_png_bytes(image_data)
        return Response(content=png, media_type="image/png")

    return app


def run(host: str = "127.0.0.1", port: int = 8501, buckets=None) -> None:
    import uvicorn

    uvicorn.run(create_app(buckets=buckets), host=host, port=port)


if __name__ == "__main__":
    run()
