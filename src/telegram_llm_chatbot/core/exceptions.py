class FileTooLargeException(Exception):
    """
    Exception raised when a file is too large.

    Attributes:
        max_file_size_mb (int): Maximum allowed file size in MB.
        message (str): Detailed message for the exception.
    """

    def __init__(self, max_file_size_mb: int = 10):
        message = f"The file is too large, the maximum size is {max_file_size_mb} MB"
        super().__init__(message)


class UnsupportedFileTypeException(Exception):
    """
    Exception raised when a file type is not supported.

    Attributes:
        file_type (str): The unsupported file type.
        supported_types (list): List of supported file types.
        message (str): Detailed message for the exception.
    """

    def __init__(self, file_type: str, supported_types: set = ("txt", "pdf", "docx")):  # noqa: D107
        message = f"File type {file_type} is not supported. Supported types: {supported_types}"
        super().__init__(message)


class TextFileDecodingException(Exception):
    """
    Exception raised when there is a decoding error while reading a text file.

    Attributes:
        message (str): Detailed message for the exception.
    """

    def __init__(self, message="Decoding error while reading the text file"):  # noqa: D107
        super().__init__(message)


class WordFileReadingException(Exception):
    """
    Exception raised when there is an error reading a Word document.

    Attributes:
        message (str): Detailed message for the exception.
    """

    def __init__(self, message="Error reading the Word document"):  # noqa: D107
        super().__init__(message)


class UnexpectedFileReadingException(Exception):
    """
    Exception raised when there is an unexpected error while reading a text file.

    Attributes:
        message (str): Detailed message for the exception.
    """

    def __init__(self, message="Unexpected error while reading the text file"):  # noqa: D107
        super().__init__(message)


class PDFFileReadingException(Exception):
    """
    Exception raised when there is an error reading a PDF file.

    Attributes:
        message (str): Detailed message for the exception.
    """

    def __init__(self, message="Error reading the PDF file"):  # noqa: D107
        super().__init__(message)
