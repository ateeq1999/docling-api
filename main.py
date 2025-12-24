from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
# from docling.document_converter import ConverterConfig
from pathlib import Path
import os
import shutil
import uuid

app = FastAPI()

TEMP_DIR = Path("temp")

@app.on_event("startup")
async def startup_event():
    """Create the temporary directory on startup."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

@app.on_event("shutdown")
async def shutdown_event():
    """Remove the temporary directory on shutdown."""
    # This is optional and can be removed if you want to keep the processed files
    # for debugging or other purposes after the server shuts down.
    # shutil.rmtree(TEMP_DIR, ignore_errors=True)
    pass

def process_document(file_path: Path, output_format: str):
    """
    Processes a document using docling and returns the output in the desired format.
    """
    config = ConverterConfig(ocr_backend="default", layout_backend="default")
    converter = DocumentConverter(config=config)

    result = converter.convert(str(file_path))

    if output_format == "text":
        return result.document.export_to_text()
    elif output_format == "markdown":
        return result.document.export_to_markdown()
    elif output_format == "json":
        # Docling's export_to_json might return a string or dict.
        # Ensure it's a dict for consistent JSON response.
        json_output = result.document.export_to_json()
        if isinstance(json_output, str):
            import json
            return json.loads(json_output)
        return json_output
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

@app.post("/upload_and_process")
async def upload_and_process(
    file: UploadFile = File(...),
    output_format: str = "markdown"  # Default to markdown
):
    """
    Uploads a document, processes it using docling, and returns the processed output.
    Supported output formats: 'text', 'markdown', 'json'.
    """
    if output_format not in ["text", "markdown", "json"]:
        raise HTTPException(
            status_code=400, detail=f"Invalid output format: {output_format}. "
            "Supported formats are 'text', 'markdown', 'json'."
        )

    temp_input_file_path = None
    try:
        # Save the uploaded file temporarily
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        temp_input_file_path = TEMP_DIR / unique_filename
        with open(temp_input_file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        processed_content = process_document(temp_input_file_path, output_format)

        if output_format == "json":
            return JSONResponse(content=processed_content)
        else:
            return {"processed_content": processed_content}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during processing: {str(e)}"
        )
    finally:
        if temp_input_file_path and temp_input_file_path.exists():
            os.remove(temp_input_file_path)

@app.post("/upload_and_save")
async def upload_and_save(
    file: UploadFile = File(...),
    output_format: str = "markdown"  # Default to markdown
):
    """
    Uploads a document, processes it using docling, and saves the processed output
    to the 'temp' directory. Supported output formats: 'text', 'markdown', 'json'.
    """
    if output_format not in ["text", "markdown", "json"]:
        raise HTTPException(
            status_code=400, detail=f"Invalid output format: {output_format}. "
            "Supported formats are 'text', 'markdown', 'json'."
        )

    temp_input_file_path = None
    output_file_path = None
    try:
        # Save the uploaded file temporarily
        unique_input_filename = f"{uuid.uuid4()}_{file.filename}"
        temp_input_file_path = TEMP_DIR / unique_input_filename
        with open(temp_input_file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        processed_content = process_document(temp_input_file_path, output_format)

        # Determine output filename and save
        original_stem = Path(file.filename).stem
        output_filename = f"{original_stem}.{output_format}"
        output_file_path = TEMP_DIR / output_filename

        if output_format == "json":
            import json
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(processed_content, f, indent=2)
        else:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(processed_content)

        return {
            "message": "File processed and saved successfully.",
            "file_path": str(output_file_path)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during processing and saving: {str(e)}"
        )
    finally:
        if temp_input_file_path and temp_input_file_path.exists():
            os.remove(temp_input_file_path)

@app.get("/processed_files_history")
async def processed_files_history():
    """
    Returns a list of all processed files currently stored in the 'temp' directory.
    """
    try:
        files = [f.name for f in TEMP_DIR.iterdir() if f.is_file()]
        return {"processed_files": files}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred while retrieving file history: {str(e)}"
        )
