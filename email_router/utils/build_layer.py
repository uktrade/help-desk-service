import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile


class LayerBuilder:
    SKIP_DIRS = ["__pycache__"]  # /PS-IGNORE

    def __init__(self) -> None:
        super().__init__()
        self.base_dir = Path(__file__).parent.parent.resolve()

    def get_files_recursively(self, path: Path):
        for item in path.iterdir():
            if item.name in self.SKIP_DIRS:
                continue
            if item.is_file():
                yield item
            if item.is_dir():
                yield from self.get_files_recursively(item)

    def package_layer(self):
        # get the layer requirements file
        requirements_file_path = self.base_dir / "lambda-layer-requirements.txt"
        # install the requirements to a temp directory
        with tempfile.TemporaryDirectory() as tempdir:
            subprocess.call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    requirements_file_path,
                    "--target",
                    tempdir,
                ]
            )
            files = [file for file in self.get_files_recursively(Path(tempdir))]
            zipfile_path = self.base_dir.parent / "layer.zip"
            with ZipFile(zipfile_path, mode="w") as zipfile:
                for file in files:
                    archive_name = str(file).replace(tempdir, "python")
                    zipfile.write(file, arcname=archive_name)
        return zipfile_path

    def upload_layer_to_aws(self, layer_file_path: Path):
        # Would be handy to have this, but there's no time right now;
        # just upload the layer manually.
        raise NotImplementedError

    def build(self):
        layer_file_path = self.package_layer()
        print(f"Layer written to {layer_file_path}.")  # /PS-IGNORE


if __name__ == "__main__":
    main = LayerBuilder()
    main.build()
