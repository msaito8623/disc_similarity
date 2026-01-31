import math
import warnings

import numpy as np

from disc_similarity.cli import _default_feature_path
from disc_similarity.similarity import simi

FEATURE_DE = _default_feature_path("feature_de.csv")
FEATURE_NL = _default_feature_path("feature_nl.csv")


def test_identical_phoneme():
    """Same single-phoneme word in both languages → similarity of 1.0."""
    result, skipped = simi(["p"], ["p"], FEATURE_DE, FEATURE_NL)
    assert len(result) == 1
    assert skipped == []
    assert math.isclose(result[0], 1.0, abs_tol=1e-9)


def test_known_pair():
    """Two different valid words return a float in (0, 1)."""
    result, skipped = simi(["pt"], ["bd"], FEATURE_DE, FEATURE_NL)
    assert len(result) == 1
    assert skipped == []
    assert 0 < result[0] < 1


def test_different_length_words():
    """Words of different lengths are padded without error."""
    result, skipped = simi(["ptk"], ["bd"], FEATURE_DE, FEATURE_NL)
    assert len(result) == 1
    assert skipped == []
    assert 0 < result[0] <= 1


def test_unknown_characters():
    """A character absent from the feature matrix produces NaN and a skipped entry."""
    # "Q" is not in either feature matrix
    result, skipped = simi(["Q"], ["p"], FEATURE_DE, FEATURE_NL)
    assert len(result) == 1
    assert np.isnan(result[0])
    assert len(skipped) == 1
    idx, word_de, word_nl, bad_de, bad_nl = skipped[0]
    assert idx == 0
    assert "Q" in bad_de


def test_multiple_pairs_mixed():
    """Mix of valid and invalid pairs; correct lengths and skipped indices."""
    vec_de = ["p", "Q", "t"]
    vec_nl = ["p", "b", "d"]
    result, skipped = simi(vec_de, vec_nl, FEATURE_DE, FEATURE_NL)
    assert len(result) == 3
    assert len(skipped) == 1
    assert skipped[0][0] == 1  # index of the bad pair
    assert math.isclose(result[0], 1.0, abs_tol=1e-9)
    assert np.isnan(result[1])
    assert isinstance(result[2], float)


def test_empty_strings():
    """Empty DISC strings: no characters to look up, result depends on implementation."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        result, skipped = simi([""], [""], FEATURE_DE, FEATURE_NL)
    assert len(result) == 1
