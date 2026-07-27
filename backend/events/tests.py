import io
import logging
import tarfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase

from events.models import Event, UploadedFile
from events.services.archive_benchmark import BENCHMARK_LOGGER_NAME


EVENT_LINE = (
    b"1 2 account-1 instance-1 10.0.0.1 10.0.0.2 "
    b"12345 443 6 10 1000 100 200 ACCEPT OK\n"
)


def make_archive(content, archive_name="events.tgz", event_file_name="events.log"):
    archive_buffer = io.BytesIO()

    with tarfile.open(fileobj=archive_buffer, mode="w:gz") as archive:
        file_info = tarfile.TarInfo(name=event_file_name)
        file_info.size = len(content)
        archive.addfile(file_info, io.BytesIO(content))

    return SimpleUploadedFile(
        archive_name,
        archive_buffer.getvalue(),
        content_type="application/gzip",
    )


class UploadInstrumentationTests(APITestCase):
    def upload_and_capture_log(self, uploaded_file):
        with self.assertLogs(BENCHMARK_LOGGER_NAME, level=logging.INFO) as logs:
            response = self.client.post(
                reverse("upload-files"),
                {"files": [uploaded_file]},
                format="multipart",
            )

        self.assertEqual(len(logs.output), 1)
        return response, logs.output[0]

    def test_successful_upload_behavior_and_benchmark_summary(self):
        response, benchmark_log = self.upload_and_capture_log(
            make_archive(EVENT_LINE)
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "1 file(s) uploaded successfully.",
                "files": ["events.log"],
            },
        )
        self.assertEqual(UploadedFile.objects.count(), 1)
        self.assertEqual(Event.objects.count(), 1)

        expected_fields = {
            "outcome": "success",
            "error_stage": "none",
            "archives": "1",
            "files": "1",
            "events": "1",
            "uploaded_file_batch_size": "500",
            "event_batch_size": "1000",
        }
        for field, value in expected_fields.items():
            self.assertIn(f"| {field}={value}", benchmark_log)

        for timing_field in (
            "archive_copy_seconds",
            "extraction_seconds",
            "parsing_seconds",
            "uploaded_file_insert_seconds",
            "event_object_creation_seconds",
            "event_insert_seconds",
            "import_seconds",
            "request_seconds",
        ):
            self.assertRegex(
                benchmark_log,
                rf"\| {timing_field}=\d+\.\d{{6}}",
            )

        self.assertNotIn("benchmark", response.json())

    def test_rejected_extension_behavior_and_failure_summary(self):
        uploaded_file = SimpleUploadedFile("events.txt", EVENT_LINE)

        response, benchmark_log = self.upload_and_capture_log(uploaded_file)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"detail": "Only .tgz and .tar.gz uploads are supported."},
        )
        self.assertIn("| outcome=failure", benchmark_log)
        self.assertIn("| error_stage=archive_validation", benchmark_log)
        self.assertEqual(UploadedFile.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)

    def test_invalid_event_file_behavior_and_failure_summary(self):
        response, benchmark_log = self.upload_and_capture_log(
            make_archive(b"invalid event line\n")
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"detail": "Invalid event file format."},
        )
        self.assertIn("| outcome=failure", benchmark_log)
        self.assertIn("| error_stage=parsing", benchmark_log)
        self.assertNotIn("invalid event line", benchmark_log)
        self.assertEqual(UploadedFile.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
