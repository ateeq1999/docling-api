"""Image extraction service for Docling documents."""

import tempfile
from pathlib import Path
from typing import Any

from PIL import Image

from core.schemas import ImageInfo


def save_pil_image(img: Image.Image, prefix: str) -> Path:
    """Save a PIL image to a temporary file."""
    tmp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".png",
        prefix=prefix,
    )
    img.save(tmp.name, format="PNG")
    tmp.close()
    return Path(tmp.name)


def extract_images_with_annotations(document: Any) -> list[ImageInfo]:
    """
    Extract images from a Docling document with annotations.
    
    Works with PDFs, DOCX, PPTX, and image inputs.
    """
    results: list[ImageInfo] = []

    for page_idx, page in document.pages.items():
        if hasattr(page, "images"):
            for img_idx, img in enumerate(page.images, start=1):
                pil_img = img.image

                path = save_pil_image(
                    pil_img,
                    prefix=f"page{page_idx}_img{img_idx}_",
                )

                bbox = getattr(img, "bbox", None)
                bbox_list = list(bbox) if bbox is not None else None

                results.append(
                    ImageInfo(
                        type="embedded",
                        page=page_idx,
                        index=img_idx,
                        width=pil_img.width,
                        height=pil_img.height,
                        bbox=bbox_list,
                        path=str(path),
                    )
                )

        if hasattr(page, "render"):
            rendered = page.render()
            if rendered:
                path = save_pil_image(
                    rendered,
                    prefix=f"page{page_idx}_render_",
                )

                results.append(
                    ImageInfo(
                        type="page_render",
                        page=page_idx,
                        width=rendered.width,
                        height=rendered.height,
                        path=str(path),
                    )
                )

    return results
