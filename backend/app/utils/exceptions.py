"""Custom exceptions mapped to standardized API error responses."""

from typing import Any, Optional


class BaseAppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details

    def to_dict(self) -> dict:
        result = {
            "error": {
                "code": self.code,
                "message": self.message,
            }
        }
        if self.details is not None:
            result["error"]["details"] = self.details
        return result


class DataValidationError(BaseAppException):
    """Validation failure during ETL or request processing."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="DATA_VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class DBConnectionError(BaseAppException):
    """Database connectivity failure."""

    def __init__(self, message: str = "Database connection unavailable", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="DATABASE_CONNECTION_ERROR",
            status_code=503,
            details=details,
        )


class DataImportError(BaseAppException):
    """Importing or parsing staging data failure."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="IMPORT_ERROR",
            status_code=400,
            details=details,
        )


class ResourceNotFoundError(BaseAppException):
    """Requested resource (e.g. student, report, file) was not found."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' was not found.",
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource": resource, "id": str(identifier)},
        )


class AnalysisError(BaseAppException):
    """Analytics computation failure."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="ANALYSIS_ERROR",
            status_code=400,
            details=details,
        )


class ReportGenerationError(BaseAppException):
    """Report or chart generation failure."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="REPORT_GENERATION_ERROR",
            status_code=500,
            details=details,
        )
