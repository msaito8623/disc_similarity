import argparse
import os
from importlib.resources import files

import pandas as pd

from .similarity import simi_betw_nl_de


def _default_feature_path(filename):
    return str(files("disc_similarity").joinpath(filename))


def main():
    parser = argparse.ArgumentParser(
        description="Compute cosine similarity between paired Dutch and German DISC transcriptions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  # CSV mode (single file with paired words)
  disc-similarity wordlist.csv --sep ";" --encoding latin-1 -o output.tsv

  # Two-file mode (one DISC transcription per line, paired by line number)
  disc-similarity de_transcriptions.txt nl_transcriptions.txt -o results.tsv
""")
    parser.add_argument("input_file", help="CSV/TSV file with paired words, or first DISC transcription file")
    parser.add_argument("input_file_2", nargs="?", default=None,
                        help="Second DISC transcription file (one per line, paired by line number)")
    parser.add_argument("--sep", default=";", help="CSV separator (default: ;)")
    parser.add_argument("--col-de", default="PhonStrsDISC_DE", help="Column name for German DISC strings")
    parser.add_argument("--col-nl", default="PhonStrsDISC_NL", help="Column name for Dutch DISC strings")
    parser.add_argument("--encoding", default="latin-1", help="File encoding (default: latin-1)")
    parser.add_argument("--feature-de", default=_default_feature_path("feature_de.csv"),
                        help="Path to German feature matrix")
    parser.add_argument("--feature-nl", default=_default_feature_path("feature_nl.csv"),
                        help="Path to Dutch feature matrix")
    parser.add_argument("--output-sep", default="\t", help="Output CSV separator (default: tab)")
    parser.add_argument("-o", "--output", default=None, help="Output file path (default: <input_stem>_with_similarity.tsv)")
    args = parser.parse_args()

    if args.input_file_2 is None:
        dat = pd.read_csv(args.input_file, sep=args.sep, encoding=args.encoding)
        vec_de = dat[args.col_de].str.replace("['\\-]", "", regex=True)
        vec_nl = dat[args.col_nl].str.replace("['\\-]", "", regex=True)
    else:
        with open(args.input_file) as f:
            vec_de = pd.Series([line.strip().replace("'", "").replace("-", "") for line in f])
        with open(args.input_file_2) as f:
            vec_nl = pd.Series([line.strip().replace("'", "").replace("-", "") for line in f])
        dat = pd.DataFrame({args.col_de: vec_de, args.col_nl: vec_nl})

    simi, skipped = simi_betw_nl_de(vec_de, vec_nl, args.feature_de, args.feature_nl)
    dat["simi"] = simi

    if args.output is None:
        stem = os.path.splitext(args.input_file)[0]
        output_path = stem + "_with_similarity.tsv"
    else:
        output_path = args.output

    dat.to_csv(output_path, sep=args.output_sep, index=False, header=True)
    print(f"Output written to {output_path}")

    if skipped:
        log_path = os.path.splitext(output_path)[0] + "_skipped.log"
        with open(log_path, "w") as log:
            header = f"{len(skipped)} word pair(s) returned NA due to unexpected characters:"
            print(header)
            log.write(header + "\n")
            for idx, word_de, word_nl, bad_de, bad_nl in skipped:
                parts = [f"  Row {idx + 1}: DE='{word_de}', NL='{word_nl}'"]
                if bad_de:
                    parts.append(f"unknown DE chars: {bad_de}")
                if bad_nl:
                    parts.append(f"unknown NL chars: {bad_nl}")
                line = " — ".join(parts)
                print(line)
                log.write(line + "\n")
        print(f"Log written to {log_path}")
