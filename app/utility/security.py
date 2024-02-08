# import magic

ALLOWED_IMAGE_EXTENSIONS = (".jpg", ".png", ".jpeg")


def is_valid_image(file_name: str, file_content: bytes):
    # file_mime = magic.from_buffer(file_content, True)
    # return file_mime.startswith("image/") and any(
        # file_name.lower().endswith(ext) for ext in ALLOWED_IMAGE_EXTENSIONS
    # )
    return any(file_name.lower().endswith(ext) for ext in ALLOWED_IMAGE_EXTENSIONS)
