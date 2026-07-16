from markitdown import MarkItDown, StreamInfo
from io import BytesIO
from pydantic import Field, Base64Bytes


def binary_document_to_markdown(
    binary_data: Base64Bytes = Field(
        description="Base64-encoded binary content of the document to convert"
    ),
    file_type: str = Field(
        description="File extension of the document, e.g. 'docx', 'pdf', 'pptx', 'xlsx'"
    ),
) -> str:
    """Convert binary document data to markdown-formatted text.

    Decodes the given file content and converts it to markdown using the
    `markitdown` library, which supports common office and document formats
    by inspecting the provided file extension.

    When to use:
    - When you have raw document bytes (not a file path) and need their
      text content as markdown, e.g. content received over MCP.
    - When you know the document's file type/extension.

    When not to use:
    - For plain text or markdown that's already readable as-is.
    - When you only have a file path; read the file into bytes first.
    - For PDFs specifically, prefer `pdf_to_markdown`.

    Examples:
    >>> with open("report.docx", "rb") as f:
    ...     data = f.read()
    >>> binary_document_to_markdown(data, "docx")  # doctest: +SKIP
    '# Report\\n...'
    """
    md = MarkItDown()
    file_obj = BytesIO(binary_data)
    stream_info = StreamInfo(extension=file_type)
    result = md.convert(file_obj, stream_info=stream_info)
    return result.text_content


def pdf_to_markdown(
    binary_data: Base64Bytes = Field(
        description="Base64-encoded binary content of the PDF file to convert"
    ),
) -> str:
    """Convert a PDF document to markdown-formatted text.

    Decodes the given PDF file content and converts it to markdown using
    `markitdown`, preserving headings, lists, and basic formatting where
    detectable in the source PDF.

    When to use:
    - When you have raw PDF bytes (not a file path) and need their text
      content as markdown, e.g. a PDF received over MCP.
    - When you need a PDF's content in a format that's easy for an LLM to read.

    When not to use:
    - For non-PDF documents; use `binary_document_to_markdown` with the
      appropriate file type instead.
    - When you only have a file path; read the file into bytes first.

    Examples:
    >>> with open("report.pdf", "rb") as f:
    ...     data = f.read()
    >>> pdf_to_markdown(data)  # doctest: +SKIP
    '# Report\\n...'
    """
    return binary_document_to_markdown(binary_data, "pdf")
