# TODO for Docling API Refactoring

## High-Priority Improvements

* **Implement true end-to-end streaming for `/process/stream` endpoint**:
* Currently, `process_document_stream` in `services/docling_service.py` processes the entire document into memory first, then streams the result.
* Investigate if `docling.document_converter.DocumentConverter` supports chunk-based processing or streaming output.
* If possible, modify `process_document_stream` to process and yield document parts concurrently, reducing memory footprint for very large files. This might involve adapting `_convert` or creating a new streaming-aware conversion function.

## Minor Improvements/Considerations

* **Error Handling Refinement**: Ensure consistent and detailed error responses across all endpoints, especially for errors originating from `docling.document_converter`.
* **Configuration Management**: If `ConverterConfig` needs to be dynamic or depend on environment variables, consider making it configurable within the `DoclingService` initialization or via FastAPI dependencies.
* **Logging**: Add more detailed logging within `docling_service.py` to track document processing progress and aid in debugging.
