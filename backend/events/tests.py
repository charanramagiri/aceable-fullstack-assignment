import io
import logging
import tarfile
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase

from events.models import Event, UploadedFile
from events.services.archive_benchmark import BENCHMARK_LOGGER_NAME


EVENT_LINE = (
    b"1 2 account-1 instance-1 10.0.0.1 10.0.0.2 "
    b"12345 443 6 10 1000 100 200 ACCEPT OK\n"
)


def make_archive(
    members,
    archive_name="events.tgz",
):
    archive_buffer = io.BytesIO()

    with tarfile.open(fileobj=archive_buffer, mode="w:gz") as archive:
        for member in members:
            archive.addfile(member["info"], member.get("stream"))

    return SimpleUploadedFile(
        archive_name,
        archive_buffer.getvalue(),
        content_type="application/gzip",
    )


def regular_member(name="events.log", content=EVENT_LINE):
    file_info = tarfile.TarInfo(name=name)
    file_info.size = len(content)
    return {"info": file_info, "stream": io.BytesIO(content)}


def directory_member(name="logs/"):
    directory_info = tarfile.TarInfo(name=name)
    directory_info.type = tarfile.DIRTYPE
    return {"info": directory_info}


def special_member(member_type, name="unsupported"):
    member_info = tarfile.TarInfo(name=name)
    member_info.type = member_type
    member_info.linkname = "events.log"
    return {"info": member_info}


class UploadStreamingTests(APITestCase):
    def upload_and_capture_log(self, uploaded_files):
        if not isinstance(uploaded_files, list):
            uploaded_files = [uploaded_files]

        with self.assertLogs(BENCHMARK_LOGGER_NAME, level=logging.INFO) as logs:
            response = self.client.post(
                reverse("upload-files"),
                {"files": uploaded_files},
                format="multipart",
            )

        self.assertEqual(len(logs.output), 1)
        return response, logs.output[0]

    def assert_invalid_archive(self, uploaded_file):
        response, benchmark_log = self.upload_and_capture_log(uploaded_file)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Invalid archive file."})
        self.assertIn("| outcome=failure", benchmark_log)
        self.assertIn("| error_stage=archive_streaming", benchmark_log)
        self.assertEqual(UploadedFile.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)

    def test_valid_tgz_upload_streams_without_copying_or_extracting(self):
        uploaded_file = make_archive([regular_member()])
        uploaded_file.chunks = lambda: (_ for _ in ()).throw(
            AssertionError("archive chunks must not be copied")
        )

        with patch.object(
            tarfile.TarFile,
            "extractall",
            side_effect=AssertionError("archive must not be extracted"),
        ):
            response, benchmark_log = self.upload_and_capture_log(uploaded_file)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "1 file(s) uploaded successfully.",
                "files": ["events.log"],
            },
        )
        self.assertEqual(
            list(UploadedFile.objects.values_list("filename", "event_count")),
            [("events.log", 1)],
        )
        self.assertEqual(Event.objects.count(), 1)
        self.assertIn("| outcome=success", benchmark_log)
        self.assertIn("| archives=1", benchmark_log)
        self.assertIn("| files=1", benchmark_log)
        self.assertIn("| events=1", benchmark_log)
        self.assertIn("| archive_copy_seconds=0.000000", benchmark_log)
        self.assertRegex(
            benchmark_log,
            r"\| archive_streaming_seconds=\d+\.\d{6}",
        )
        for timing_field in (
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
        self.assertIn("| uploaded_file_batch_size=500", benchmark_log)
        self.assertIn("| event_batch_size=1000", benchmark_log)
        self.assertNotIn("benchmark", response.json())

    def test_valid_tar_gz_upload_preserves_filename_and_event_count(self):
        response, _ = self.upload_and_capture_log(
            make_archive(
                [regular_member("nested/events.log", EVENT_LINE * 2)],
                archive_name="events.tar.gz",
            )
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["files"], ["events.log"])
        self.assertEqual(
            list(UploadedFile.objects.values_list("filename", "event_count")),
            [("events.log", 2)],
        )
        self.assertEqual(Event.objects.count(), 2)

    def test_multiple_archives_are_processed_in_request_order(self):
        first_archive = make_archive(
            [regular_member("first.log")],
            archive_name="first.tgz",
        )
        second_archive = make_archive(
            [regular_member("second.log", EVENT_LINE * 2)],
            archive_name="second.tar.gz",
        )

        response, benchmark_log = self.upload_and_capture_log(
            [first_archive, second_archive]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["files"], ["first.log", "second.log"])
        self.assertEqual(
            list(UploadedFile.objects.values_list("filename", "event_count")),
            [("first.log", 1), ("second.log", 2)],
        )
        self.assertEqual(Event.objects.count(), 3)
        self.assertIn("| archives=2", benchmark_log)
        self.assertIn("| files=2", benchmark_log)
        self.assertIn("| events=3", benchmark_log)

    def test_plain_file_is_rejected(self):
        uploaded_file = SimpleUploadedFile("events.txt", EVENT_LINE)

        response, benchmark_log = self.upload_and_capture_log(uploaded_file)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"detail": "Only .tgz and .tar.gz uploads are supported."},
        )
        self.assertIn("| error_stage=archive_validation", benchmark_log)

    def test_empty_archive_is_rejected(self):
        self.assert_invalid_archive(make_archive([]))

    def test_corrupt_archive_is_rejected(self):
        self.assert_invalid_archive(
            SimpleUploadedFile(
                "corrupt.tgz",
                b"not a gzip archive",
                content_type="application/gzip",
            )
        )

    def test_directories_are_ignored_and_regular_files_succeed(self):
        response, _ = self.upload_and_capture_log(
            make_archive(
                [
                    directory_member(),
                    regular_member("logs/events.log"),
                ]
            )
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["files"], ["events.log"])
        self.assertEqual(UploadedFile.objects.get().event_count, 1)

    def test_symbolic_link_is_rejected(self):
        self.assert_invalid_archive(
            make_archive([special_member(tarfile.SYMTYPE, "link")])
        )

    def test_hard_link_is_rejected(self):
        self.assert_invalid_archive(
            make_archive([special_member(tarfile.LNKTYPE, "hard-link")])
        )

    def test_special_member_is_rejected(self):
        self.assert_invalid_archive(
            make_archive([special_member(tarfile.CHRTYPE, "device")])
        )

    def test_invalid_event_file_rolls_back_complete_request(self):
        response, benchmark_log = self.upload_and_capture_log(
            make_archive(
                [
                    regular_member("valid.log"),
                    regular_member("invalid.log", b"invalid event line\n"),
                ]
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"detail": "Invalid event file format."},
        )
        self.assertIn("| error_stage=parsing", benchmark_log)
        self.assertEqual(UploadedFile.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
