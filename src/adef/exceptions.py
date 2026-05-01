class ADEFError(Exception):
    pass


class IngestionError(ADEFError):
    pass


class ValidationError(ADEFError):
    pass


class TransformationError(ADEFError):
    pass


class QualityError(ADEFError):
    pass


class MetadataStoreError(ADEFError):
    pass


class LineageError(ADEFError):
    pass


class PipelineError(ADEFError):
    pass
