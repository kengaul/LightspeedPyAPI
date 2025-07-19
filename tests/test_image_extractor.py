import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from image_extractor import pdf_to_text


class DummyCompleted:
    def __init__(self, stdout=''):
        self.stdout = stdout


def test_pdf_to_text(monkeypatch, tmp_path):
    pdf = tmp_path / "file.pdf"
    pdf.write_bytes(b"%PDF-1.4")

    def fake_run(cmd, check, capture_output, text):
        assert cmd[0] == "pdftotext"
        assert cmd[1] == str(pdf)
        assert check and capture_output and text
        return DummyCompleted(stdout="example text")

    monkeypatch.setattr('subprocess.run', fake_run)
    result = pdf_to_text(pdf)
    assert result == "example text"
