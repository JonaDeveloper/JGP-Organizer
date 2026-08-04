
# Dictionary that maps file extensions to their corresponding categories.

classify = {
    # Image file formats.
    '.jpg': 'Images',
    '.jpeg': 'Images',
    '.png': 'Images',
    '.webp': 'Images',
    '.gif': 'Images',
    '.bmp': 'Images',
    '.tiff': 'Images',
    '.svg': 'Images',
    '.heic': 'Images',
    '.raw': 'Images',

    # Document file formats.
    '.pdf': 'Documents',
    '.docx': 'Documents',
    '.doc': 'Documents',
    '.txt': 'Documents',
    '.rtf': 'Documents',
    '.odt': 'Documents',
    '.md': 'Documents',
    '.pages': 'Documents',
    '.tex': 'Documents',
    '.epub': 'Documents',

    # Compressed archive file formats.
    '.zip': 'Compress',
    '.rar': 'Compress',
    '.7z': 'Compress',
    '.tar': 'Compress',
    '.gz': 'Compress',
    '.bz2': 'Compress',
    '.xz': 'Compress',
    '.iso': 'Compress',
    '.cab': 'Compress',
    '.zst': 'Compress',

    # Installer and application package formats.
    '.exe': 'Installers',
    '.msi': 'Installers',
    '.app': 'Installers',
    '.pkg': 'Installers',
    '.dmg': 'Installers',
    '.deb': 'Installers',
    '.rpm': 'Installers',
    '.apk': 'Installers',
    '.ipa': 'Installers',
    '.appimage': 'Installers',

    # Audio file formats.
    '.mp3': 'Audio',
    '.wav': 'Audio',
    '.flac': 'Audio',
    '.aac': 'Audio',
    '.ogg': 'Audio',
    '.m4a': 'Audio',
    '.wma': 'Audio',
    '.aiff': 'Audio',
    '.opus': 'Audio',
    '.mid': 'Audio',

    # Video file formats.
    '.mp4': 'Video',
    '.mkv': 'Video',
    '.avi': 'Video',
    '.mov': 'Video',
    '.wmv': 'Video',
    '.webm': 'Video',
    '.flv': 'Video',
    '.mpeg': 'Video',
    '.3gp': 'Video',
    '.m4v': 'Video',
}

# Default category assigned to files with unrecognized extensions.
unclassified = 'Others'