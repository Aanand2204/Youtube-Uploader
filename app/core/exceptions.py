class PipelineError(Exception):
    """Raised when a pipeline step fails. Carries the step name for diagnosis."""

    def __init__(self, step: str, cause: Exception) -> None:
        self.step = step
        self.cause = cause
        super().__init__(f"Pipeline failed at step '{step}': {cause}")
