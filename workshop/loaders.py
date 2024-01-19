from pathlib import Path

from langchain_community.document_loaders.blob_loaders.schema import Blob, BlobLoader
from langchain_community.document_loaders.helpers import detect_file_encodings

class FileSystemModel():
    def __init__(
        self,
        path,
        includes=['**/*'],
        suffixes=[],
        excludes=[],
        excludes_matching=[]
    ):
        if isinstance(path, Path):
            _path = path
        elif isinstance(path, str):
            _path = Path(path)
        else:
            raise TypeError(f"Expected str or Path, got {type(path)}")
        
        self.path = _path.expanduser()
        self.includes = includes
        self.suffixes = suffixes
        self.excludes = excludes
        self.excludes_matching = excludes_matching

    def yield_paths(self):
        excluded_paths = self._yield_exclude_globs()

        for include_glob in self.includes:
            for path in self.path.glob(include_glob):
                if self.excludes:
                    if path in excluded_paths:
                        continue
                if self.excludes_matching:
                    if any(pattern in str(path) for pattern in self.excludes_matching):
                        continue
                if path.is_file():
                    if self.suffixes and path.suffix not in self.suffixes:
                        continue
                    yield path

    def _yield_exclude_globs(self):
        for exclude_glob in self.excludes:
            for path in self.path.glob(exclude_glob):
                if path.is_file():
                    yield path

class TextBlobListLoader(BlobLoader):
    def __init__(
        self,
        paths,
        encoding = 'utf-8',
        autodetect_encoding = True
    ):
        self.paths = paths
        self.encoding = encoding
        self.autodetect_encoding = autodetect_encoding

    def yield_blobs(self):
        for path in self.paths:
            yield self.yield_blob(path)

    def yield_blob(self, file_path):
        """Load from file path."""
        text = ""
        enc = self.encoding
        try:
            with open(file_path, encoding=self.encoding) as f:
                text = f.read()
        except UnicodeDecodeError as e:
            if self.autodetect_encoding:
                detected_encodings = detect_file_encodings(file_path)
                for encoding in detected_encodings:
                    try:
                        with open(file_path, encoding=encoding.encoding) as f:
                            text = f.read()
                            enc = encoding.encoding
                        break
                    except UnicodeDecodeError:
                        continue
            else:
                raise RuntimeError(f"Error loading {file_path}") from e
        except Exception as e:
            raise RuntimeError(f"Error loading {file_path}") from e

        return Blob.from_data(text, encoding=enc, path=file_path)

class TextBlobLoader(BlobLoader):
    def __init__(
        self,
        path,
        glob = '**/*',
        exclude = [],
        suffixes = None,
        encoding = None,
        autodetect_encoding = True,
    ):
        """Initialize with file path."""
        if isinstance(path, Path):
            _path = path
        elif isinstance(path, str):
            _path = Path(path)
        else:
            raise TypeError(f"Expected str or Path, got {type(path)}")

        self.path = _path.expanduser()  # Expand user to handle ~
        self.glob = glob
        self.suffixes = set(suffixes or [])
        self.exclude = exclude
        self.encoding = encoding
        self.autodetect_encoding = autodetect_encoding

    def yield_blobs(self):
        paths = self.path.glob(self.glob)
        for path in paths:
            if self.exclude:
                if any(glob in str(path) for glob in self.exclude):
                    continue
            if path.is_file():
                if self.suffixes and path.suffix not in self.suffixes:
                    continue
                yield self.yield_blob(path)

    def yield_blob(self, file_path):
        """Load from file path."""
        text = ""
        enc = self.encoding
        try:
            with open(file_path, encoding=self.encoding) as f:
                text = f.read()
        except UnicodeDecodeError as e:
            if self.autodetect_encoding:
                detected_encodings = detect_file_encodings(file_path)
                for encoding in detected_encodings:
                    try:
                        with open(file_path, encoding=encoding.encoding) as f:
                            text = f.read()
                            enc = encoding.encoding
                        break
                    except UnicodeDecodeError:
                        continue
            else:
                raise RuntimeError(f"Error loading {file_path}") from e
        except Exception as e:
            raise RuntimeError(f"Error loading {file_path}") from e

        return Blob.from_data(text, encoding=enc, path=file_path)