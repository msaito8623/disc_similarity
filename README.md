# disc_similarity

Compute cosine similarity between paired Dutch and German phonemic
transcriptions in DISC encoding, using phonemic feature vectors.

Each phoneme is represented as a binary feature vector (place/manner of
articulation, voicing, vowel height/backness, etc.). Word-level vectors are
formed by concatenating the feature vectors of their constituent phonemes,
zero-padded to equal length. Similarity is then computed as the cosine
similarity between these word-level vectors.


## Installation

```bash
git clone https://github.com/msaito8623/disc_similarity.git
cd disc_similarity
```

### pip

```bash
pip install .
```

### uv

```bash
uv pip install .
```

### conda

Activate your conda environment, then install with pip:

```bash
conda activate myenv
pip install .
```

For development (editable install), replace `install .` with `install -e .` in any of the above commands.

## Usage

### CLI

#### CSV mode

Process a single CSV/TSV file containing paired Dutch and German DISC transcriptions:

```bash
disc-similarity wordlist.csv --sep ";" --encoding latin-1 -o output.tsv
```

Options:

- `--sep` — input CSV separator (default: `;`)
- `--col-de` — column name for German DISC strings (default: `PhonStrsDISC_DE`)
- `--col-nl` — column name for Dutch DISC strings (default: `PhonStrsDISC_NL`)
- `--encoding` — input file encoding (default: `latin-1`)

#### Two-file mode

Provide two plain-text files, each containing one DISC transcription per line, paired by line number:

```bash
disc-similarity de_transcriptions.txt nl_transcriptions.txt -o results.tsv
```

#### Common options

- `-o`, `--output` — output file path (default: `<input_stem>_with_similarity.tsv`)
- `--output-sep` — output CSV separator (default: tab)
- `--feature-de` — path to German feature matrix (default: bundled `feature_de.csv`)
- `--feature-nl` — path to Dutch feature matrix (default: bundled `feature_nl.csv`)

### Python API

```python
from disc_similarity import simi

similarities, skipped = simi(
    vec_de=["pakt", "hUnt"],
    vec_nl=["pAkt", "hOnt"],
    feature_de_path="path/to/feature_de.csv",
    feature_nl_path="path/to/feature_nl.csv",
)
```

## Feature matrix format

The feature matrices (`feature_de.csv`, `feature_nl.csv`) are tab-separated files. Each row is a DISC phoneme symbol, and each column is a binary articulatory feature:

| consonant | example | bilabial | labiodental | alveolar | ... |
|-----------|---------|----------|-------------|----------|-----|
| p         | Pakt    | 1        |             |          | ... |


## License

MIT
