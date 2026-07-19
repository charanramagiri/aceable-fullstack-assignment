import os
from django.conf import settings


def save_uploaded_files(files):
    """
    Save uploaded files to MEDIA_ROOT.
    Returns a list of saved filenames.
    """

    saved_files = []

    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    for file in files:
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)

        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        saved_files.append(file.name)

    return saved_files