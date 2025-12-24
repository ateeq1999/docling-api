from fastapi import FastAPI, UploadFile, File, HTTPException
from docling.document_converter import DocumentConverter, ConverterConfig
from pathlib import Path

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/convert_pdf_to_markdown/")
async def convert_pdf_to_markdown(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")

    try:
        temp_file_path = Path(f"./temp_{file.filename}")
        with open(temp_file_path, "wb") as f:
            f.write(await file.read())

        config = ConverterConfig(ocr_backend="default", layout_backend="default")
        converter = DocumentConverter(config=config)

        result = converter.convert(str(temp_file_path))
        markdown_output = result.document.export_to_markdown()

        temp_file_path.unlink()

        return {"markdown": markdown_output}

    except Exception as e:
        if temp_file_path.exists():
            temp_file_path.unlink()
        raise HTTPException(status_code=500, detail=f"An error occurred during conversion: {str(e)}")