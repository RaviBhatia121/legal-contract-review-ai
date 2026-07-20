import uuid

from fastapi import HTTPException


class ApiError(HTTPException):
    def __init__(self, status_code: int, code: str, message: str, retryable: bool = False):
        self.code = code
        self.retryable = retryable
        self.request_id = str(uuid.uuid4())
        super().__init__(
            status_code=status_code,
            detail={
                "error": {
                    "code": code,
                    "message": message,
                    "retryable": retryable,
                    "request_id": self.request_id,
                }
            },
        )


def unsupported_file_type() -> ApiError:
    return ApiError(400, "UNSUPPORTED_FILE_TYPE", "Upload a PDF or DOCX file.")


def file_too_large() -> ApiError:
    return ApiError(400, "FILE_TOO_LARGE", "The file exceeds the 15 MB upload limit.")


def encrypted_document() -> ApiError:
    return ApiError(400, "ENCRYPTED_DOCUMENT", "Encrypted or password-protected documents are not supported.")


def document_too_long() -> ApiError:
    return ApiError(400, "DOCUMENT_TOO_LONG", "The document exceeds the 100-page processing limit.")


def document_parse_failed() -> ApiError:
    return ApiError(400, "DOCUMENT_PARSE_FAILED", "The document could not be parsed.", retryable=True)


def no_reviewable_text() -> ApiError:
    return ApiError(400, "NO_REVIEWABLE_TEXT", "No reviewable text was found in this document.")


def document_not_applicable() -> ApiError:
    return ApiError(400, "DOCUMENT_NOT_APPLICABLE", "This document does not appear to be a reviewable contract.")


def model_timeout() -> ApiError:
    return ApiError(504, "MODEL_TIMEOUT", "The model provider did not respond in time.", retryable=True)


def model_output_invalid() -> ApiError:
    return ApiError(
        502, "MODEL_OUTPUT_INVALID", "The review could not produce a valid structured result.", retryable=True
    )


def provider_unavailable() -> ApiError:
    return ApiError(503, "PROVIDER_UNAVAILABLE", "The configured model provider is unavailable.", retryable=True)


def review_not_found() -> ApiError:
    return ApiError(404, "REVIEW_NOT_FOUND", "No review exists for this identifier.")


def review_expired() -> ApiError:
    return ApiError(410, "REVIEW_EXPIRED", "This review has expired under retention policy.")


def configuration_invalid(message: str) -> ApiError:
    return ApiError(400, "CONFIGURATION_INVALID", message)
