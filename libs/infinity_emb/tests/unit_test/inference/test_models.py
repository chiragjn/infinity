"""
Tests that the pretrained models produce the correct scores on the STSbenchmark dataset
"""
import copy
from typing import List

import pytest
import torch
from sentence_transformers import InputExample  # type: ignore
from sentence_transformers.evaluation import (  # type: ignore
    EmbeddingSimilarityEvaluator,  # type: ignore
)

from infinity_emb.inference.models import (
    CT2SentenceTransformer,
    SentenceTransformerPatched,
)


def _pretrained_model_score(
    dataset: List[InputExample],
    model_name,
    expected_score,
    ct2_compute_type: str = "",
    device: str = "cuda",
):
    test_samples = dataset[::3]

    if ct2_compute_type:
        model = CT2SentenceTransformer(model_name, compute_type=ct2_compute_type)
        if not torch.cuda.is_available() or device == "cpu":
            model.to("cpu")
        else:
            model.to("cuda")

    else:
        model = SentenceTransformerPatched(model_name)
    evaluator = EmbeddingSimilarityEvaluator.from_input_examples(
        test_samples, name="sts-test"
    )

    score = model.evaluate(evaluator) * 100
    print(model_name, "{:.2f} vs. exp: {:.2f}".format(score, expected_score))
    assert score > expected_score or abs(score - expected_score) < 0.1


@pytest.mark.parametrize(
    "model,score,compute_type,device",
    [
        ("sentence-transformers/bert-base-nli-mean-tokens", 76.76, "int8", "cuda"),
        ("sentence-transformers/bert-base-nli-mean-tokens", 76.86, None, "cuda"),
        ("sentence-transformers/all-MiniLM-L6-v2", 82.03, None, "cuda"),
        ("sentence-transformers/all-MiniLM-L6-v2", 82.03, "default", "cuda"),
        ("sentence-transformers/all-MiniLM-L6-v2", 81.73, "int8", "cuda"),
        ("sentence-transformers/all-MiniLM-L6-v2", 82.03, "default", "cpu"),
    ],
)
def test_bert(get_sts_bechmark_dataset, model, score, compute_type, device):
    samples = copy.deepcopy(get_sts_bechmark_dataset[2])
    _pretrained_model_score(
        samples, model, score, ct2_compute_type=compute_type, device=device
    )