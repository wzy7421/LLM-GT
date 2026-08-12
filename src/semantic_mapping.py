#!/usr/bin/env python3
"""Paper-aligned semantic-mapping demonstration.

This script mirrors the manuscript's computational scaffold:
SentenceTransformer embeddings -> UMAP -> HDBSCAN -> class-based TF-IDF.

Important boundaries
--------------------
- No generative LLM is used for clustering.
- Cluster membership is determined before any LLM-assisted interpretation.
- The exported clusters, terms, and outlier flags are provisional computational
  scaffolds rather than final theoretical categories or research-gap claims.
- Demo CSVs are synthetic schema examples only and are not the empirical corpora.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import hdbscan
import numpy as np
import pandas as pd
import yaml
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_documents(df: pd.DataFrame, corpus: str) -> pd.Series:
    if corpus == "academic":
        required = ["title", "abstract", "keywords"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Academic input missing columns: {missing}")
        return (
            df["title"].fillna("").astype(str)
            + ". "
            + df["abstract"].fillna("").astype(str)
            + ". Keywords: "
            + df["keywords"].fillna("").astype(str)
        )

    if "text" not in df.columns:
        raise ValueError("Public input must contain a 'text' column")
    return df["text"].fillna("").astype(str)


def class_tfidf_top_terms(
    documents: pd.Series,
    labels: np.ndarray,
    top_n: int = 10,
    stop_words: str | None = "english",
) -> dict[int, list[str]]:
    """Return top terms from a compact class-based TF-IDF representation.

    Documents assigned to the same HDBSCAN cluster are concatenated into one
    class document. Term frequency is L1-normalized within each class. The IDF
    factor uses the average number of words per class divided by corpus-wide
    term frequency, following the class-based representation used by the
    BERTopic family. This is an inspectable implementation rather than a claim
    of algorithmic novelty.

    Noise points (cluster -1) are intentionally excluded from class-term
    generation but remain present in the exported document-level audit table.
    """
    tmp = pd.DataFrame({"document": documents, "cluster": labels})
    tmp = tmp[tmp["cluster"] != -1]
    if tmp.empty:
        return {}

    class_docs = tmp.groupby("cluster", sort=True)["document"].apply(" ".join)
    vectorizer = CountVectorizer(stop_words=stop_words)
    matrix = vectorizer.fit_transform(class_docs.values)

    counts = matrix.toarray().astype(float)
    class_lengths = counts.sum(axis=1, keepdims=True)
    class_lengths[class_lengths == 0] = 1.0
    tf = counts / class_lengths

    term_frequency = counts.sum(axis=0)
    term_frequency[term_frequency == 0] = 1.0
    average_words_per_class = float(counts.sum(axis=1).mean())
    idf = np.log1p(average_words_per_class / term_frequency)
    scores = tf * idf

    vocab = np.asarray(vectorizer.get_feature_names_out())
    output: dict[int, list[str]] = {}
    for row_idx, cluster_id in enumerate(class_docs.index):
        order = np.argsort(scores[row_idx])[::-1][:top_n]
        output[int(cluster_id)] = vocab[order].tolist()
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--corpus", choices=["academic", "public"], required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--config", default="config/paper_config.yaml")
    parser.add_argument(
        "--embedding-model",
        default=None,
        help="Optional model override for sensitivity checks; primary paper model is used by default.",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    df = pd.read_csv(args.input)
    documents = build_documents(df, args.corpus)

    model_name = args.embedding_model or cfg["embedding"]["model"]
    model = SentenceTransformer(model_name)
    embeddings = model.encode(
        documents.tolist(),
        normalize_embeddings=cfg["embedding"].get("normalize_embeddings", True),
        show_progress_bar=True,
    )

    umap_cfg = cfg["umap"]
    reducer = UMAP(
        n_neighbors=umap_cfg["n_neighbors"],
        min_dist=umap_cfg["min_dist"],
        n_components=umap_cfg["n_components"],
        metric=umap_cfg["metric"],
        random_state=umap_cfg["random_state"],
    )
    reduced = reducer.fit_transform(embeddings)

    hcfg = cfg["hdbscan"][args.corpus]
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=hcfg["min_cluster_size"],
        min_samples=hcfg["min_samples"],
        metric=hcfg["metric"],
        cluster_selection_method=hcfg["cluster_selection_method"],
    )
    labels = clusterer.fit_predict(reduced)

    terms = class_tfidf_top_terms(
        documents,
        labels,
        top_n=cfg["ctfidf"]["top_n_terms"],
        stop_words=cfg["ctfidf"].get("stop_words", "english"),
    )

    out = df.copy()
    out["embedding_model"] = model_name
    out["cluster"] = labels
    out["is_outlier"] = labels == -1
    out["top_c_tfidf_terms"] = [
        "; ".join(terms.get(int(label), [])) if label != -1 else ""
        for label in labels
    ]

    for i in range(reduced.shape[1]):
        out[f"umap_dim_{i + 1}"] = reduced[:, i]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_outliers = int((labels == -1).sum())
    print(f"Saved: {output_path}")
    print(f"Embedding model: {model_name}")
    print(f"Clusters: {n_clusters}; HDBSCAN outlier/noise flags: {n_outliers}")
    print("Reminder: these outputs are provisional computational scaffolds, not findings.")


if __name__ == "__main__":
    main()
