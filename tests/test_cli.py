import os
import subprocess
import sys
import tempfile


def test_help_exits_zero():
    result = subprocess.run(
        ["disc-similarity", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_two_file_mode():
    with tempfile.TemporaryDirectory() as tmp:
        de_path = os.path.join(tmp, "de.txt")
        nl_path = os.path.join(tmp, "nl.txt")
        out_path = os.path.join(tmp, "out.tsv")

        with open(de_path, "w") as f:
            f.write("p\nt\n")
        with open(nl_path, "w") as f:
            f.write("p\nd\n")

        result = subprocess.run(
            ["disc-similarity", de_path, nl_path, "-o", out_path],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert os.path.exists(out_path)

        import pandas as pd
        df = pd.read_csv(out_path, sep="\t")
        assert "simi" in df.columns
        assert len(df) == 2
