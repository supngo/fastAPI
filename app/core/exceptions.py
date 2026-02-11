class AppError(Exception):
    """Base class for all application errors"""
    pass


class NotFoundError(AppError):
    pass


class ValidationError(AppError):
    pass


class ConflictError(AppError):
    pass

class UnauthorizedError(AppError):
    pass

class ForbiddenError(AppError):
    pass
