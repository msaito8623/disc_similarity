import argparse
import os

import pandas as pd
import numpy as np
import xarray as xr
import scipy.spatial.distance as dist


def simi_betw_nl_de(vec_de, vec_nl, feature_de_path, feature_nl_path):
    vde = pd.Series(vec_de)
    vnl = pd.Series(vec_nl)

    matD = pd.read_csv(feature_de_path, sep="\t", header=0).fillna(0)
    matD = matD.set_index("consonant").drop(columns=["example"]).astype(int)
    matD = xr.DataArray(matD, dims=("consonant", "feature"), coords={"consonant": matD.index, "feature": matD.columns})
    matN = pd.read_csv(feature_nl_path, sep="\t", header=0).fillna(0)
    matN = matN.set_index("consonant").drop(columns=["example"]).astype(int)
    matN = xr.DataArray(matN, dims=("consonant", "feature"), coords={"consonant": matN.index, "feature": matN.columns})

    valid_de = set(matD.consonant.values)
    valid_nl = set(matN.consonant.values)

    simi = []
    skipped = []
    for idx, (word_de, word_nl) in enumerate(zip(vde, vnl)):
        bad_de = set(word_de) - valid_de
        bad_nl = set(word_nl) - valid_nl
        if bad_de or bad_nl:
            simi.append(np.nan)
            skipped.append((idx, word_de, word_nl, bad_de, bad_nl))
            continue
        phon_de = matD.loc[list(word_de), :].values.flatten()
        phon_nl = matN.loc[list(word_nl), :].values.flatten()
        xlen = max(phon_de.size, phon_nl.size)
        phon_de = np.pad(phon_de, (0, xlen - phon_de.size), mode="constant", constant_values=0)
        phon_nl = np.pad(phon_nl, (0, xlen - phon_nl.size), mode="constant", constant_values=0)
        simi.append(1 - dist.cosine(phon_de, phon_nl))
    return simi, skipped


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compute cosine similarity between paired Dutch and German DISC transcriptions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  # CSV mode (single file with paired words)
  python main.py ../data/Wordlist.csv --sep ";" --encoding latin-1 -o ../data/Wordlist_with_similarity.csv

  # Two-file mode (one DISC transcription per line, paired by line number)
  python main.py de_transcriptions.txt nl_transcriptions.txt -o results.tsv
""")
    parser.add_argument("input_file", help="CSV/TSV file with paired words, or first DISC transcription file")
    parser.add_argument("input_file_2", nargs="?", default=None,
                        help="Second DISC transcription file (one per line, paired by line number)")
    parser.add_argument("--sep", default=";", help="CSV separator (default: ;)")
    parser.add_argument("--col-de", default="PhonStrsDISC_DE", help="Column name for German DISC strings")
    parser.add_argument("--col-nl", default="PhonStrsDISC_NL", help="Column name for Dutch DISC strings")
    parser.add_argument("--encoding", default="latin-1", help="File encoding (default: latin-1)")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parser.add_argument("--feature-de", default=os.path.join(script_dir, "feature_de.csv"), help="Path to German feature matrix")
    parser.add_argument("--feature-nl", default=os.path.join(script_dir, "feature_nl.csv"), help="Path to Dutch feature matrix")
    parser.add_argument("--output-sep", default="\t", help="Output CSV separator (default: tab)")
    parser.add_argument("-o", "--output", default=None, help="Output file path (default: <input_stem>_with_similarity.tsv)")
    args = parser.parse_args()

    if args.input_file_2 is None:
        # CSV mode: single file with paired words
        dat = pd.read_csv(args.input_file, sep=args.sep, encoding=args.encoding)
        vec_de = dat[args.col_de].str.replace("['\\-]", "", regex=True)
        vec_nl = dat[args.col_nl].str.replace("['\\-]", "", regex=True)
    else:
        # Two-file mode: one DISC transcription per line
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
