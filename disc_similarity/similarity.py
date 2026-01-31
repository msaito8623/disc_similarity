import numpy as np
import pandas as pd
import scipy.spatial.distance as dist
import xarray as xr


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
