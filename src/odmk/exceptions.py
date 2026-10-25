"""Typed failures used by the command-line gates and cell engine."""


class ODMKError(RuntimeError):
    """Base exception for an invalid ODMK analysis state."""


class RegistryError(ODMKError):
    """The machine-readable preregistration is invalid or unexpected."""


class DataValidationError(ODMKError):
    """The source data fail a preregistered integrity condition."""


class ApprovalError(ODMKError):
    """Production execution has not passed the approval gate."""


class CellEstimationError(ODMKError):
    """A registered specification cannot be estimated as written."""

