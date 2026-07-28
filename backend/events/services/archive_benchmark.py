from dataclasses import dataclass


BENCHMARK_LOGGER_NAME = "events.archive_import.benchmark"


@dataclass
class ArchiveImportMetrics:
    uploaded_file_batch_size: int
    event_batch_size: int
    outcome: str = "failure"
    error_stage: str = "request"
    archives: int = 0
    files: int = 0
    events: int = 0
    duplicate_existing_filename_count: int = 0
    archive_copy_seconds: float = 0.0
    archive_streaming_seconds: float = 0.0
    duplicate_check_seconds: float = 0.0
    parsing_seconds: float = 0.0
    uploaded_file_insert_seconds: float = 0.0
    event_object_creation_seconds: float = 0.0
    event_insert_seconds: float = 0.0
    import_seconds: float = 0.0
    request_seconds: float = 0.0

    def summary(self):
        return (
            "Archive import benchmark"
            f" | outcome={self.outcome}"
            f" | error_stage={self.error_stage}"
            f" | archives={self.archives}"
            f" | files={self.files}"
            f" | events={self.events}"
            f" | duplicate_existing_filename_count={self.duplicate_existing_filename_count}"
            f" | archive_copy_seconds={self.archive_copy_seconds:.6f}"
            f" | archive_streaming_seconds={self.archive_streaming_seconds:.6f}"
            f" | duplicate_check_seconds={self.duplicate_check_seconds:.6f}"
            f" | parsing_seconds={self.parsing_seconds:.6f}"
            f" | uploaded_file_insert_seconds={self.uploaded_file_insert_seconds:.6f}"
            f" | event_object_creation_seconds={self.event_object_creation_seconds:.6f}"
            f" | event_insert_seconds={self.event_insert_seconds:.6f}"
            f" | import_seconds={self.import_seconds:.6f}"
            f" | request_seconds={self.request_seconds:.6f}"
            f" | uploaded_file_batch_size={self.uploaded_file_batch_size}"
            f" | event_batch_size={self.event_batch_size}"
        )
