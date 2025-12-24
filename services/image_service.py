import tempfile
from pathlib import Path
from typing import List, Dict

from PIL import Image


# -------------------------
# Helpers
# -------------------------

def save_pil_image(img: Image.Image, prefix: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".png",
        prefix=prefix,
    )
    img.save(tmp.name, format="PNG")
    tmp.close()  # 🔥 important on Windows
    return Path(tmp.name)


# -------------------------
# Image extraction
# -------------------------

def extract_images_with_annotations(document) -> List[Dict]:
    """
    Extract images from a Docling document with annotations.
    Works with PDFs, DOCX, PPTX, and image inputs.
    """

    results: List[Dict] = []

    # ✅ Docling pages are a dict[int, Page]
    for page_idx, page in document.pages.items():

        # -------------------------
        # Embedded images
        # -------------------------
        if hasattr(page, "images"):
            for img_idx, img in enumerate(page.images, start=1):
                pil_img = img.image

                path = save_pil_image(
                    pil_img,
                    prefix=f"page{page_idx}_img{img_idx}_",
                )

                results.append({
                    "type": "embedded",
                    "page": page_idx,
                    "index": img_idx,
                    "width": pil_img.width,
                    "height": pil_img.height,
                    "bbox": getattr(img, "bbox", None),
                    "path": str(path),
                })

        # -------------------------
        # Full page render
        # -------------------------
        if hasattr(page, "render"):
            rendered = page.render()
            if rendered:
                path = save_pil_image(
                    rendered,
                    prefix=f"page{page_idx}_render_",
                )

                results.append({
                    "type": "page_render",
                    "page": page_idx,
                    "width": rendered.width,
                    "height": rendered.height,
                    "path": str(path),
                })

    return results
