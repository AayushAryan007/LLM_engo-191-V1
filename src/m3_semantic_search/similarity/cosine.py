"""Cosine similarity, implemented from scratch.

Cosine similarity measures the angle between two vectors, ignoring their
magnitude. It answers "do these point in the same direction?" — which is what we
want for embeddings, where *direction* encodes meaning and length does not.

    cosine(A, B) = (A . B) / (|A| * |B|)

where
    A . B   = sum(a_i * b_i)            (dot product)
    |A|     = sqrt(sum(a_i * a_i))      (Euclidean magnitude / L2 norm)

The result lies in [-1, 1]: 1.0 = identical direction (most similar),
0.0 = orthogonal (unrelated), -1.0 = opposite. Kept dependency-free and in its
own module so it stays pure math — no knowledge of documents, storage, or the
embedding provider.
"""

import math


def cosine_similarity(vector1: list[float], vector2: list[float]) -> float:
    """Return the cosine similarity between two equal-length vectors.

    :param vector1: First vector.
    :param vector2: Second vector.
    :returns: Cosine similarity in the range [-1, 1]; 0.0 if either vector has
        zero magnitude.
    :raises ValueError: If the vectors are empty or of differing lengths.
    """
    if not vector1 or not vector2:
        raise ValueError("Vectors must be non-empty.")
    if len(vector1) != len(vector2):
        raise ValueError(
            f"Vectors must be the same length: {len(vector1)} != {len(vector2)}"
        )

    # Dot product: how much the two vectors "agree" component by component.
    dot_product = sum(a * b for a, b in zip(vector1, vector2))

    # Magnitudes: the length of each vector, used to normalize the dot product
    # so only direction (not scale) affects the result.
    magnitude1 = math.sqrt(sum(a * a for a in vector1))
    magnitude2 = math.sqrt(sum(b * b for b in vector2))

    # A zero-magnitude vector has no direction, so similarity is undefined;
    # return 0.0 rather than dividing by zero.
    if magnitude1 == 0.0 or magnitude2 == 0.0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


if __name__ == "__main__":
    # Demonstration only: illustrative hand-crafted vectors (not real
    # embeddings) chosen so the relationships mirror what real embeddings show.
    python_a = [1.0, 1.0, 0.0, 0.0]
    python_b = [1.0, 1.0, 0.0, 0.0]  # same topic -> identical direction
    django = [1.0, 0.3, 0.4, 0.0]  # related (both Python web) -> close
    redis = [0.4, 0.5, 1.0, 0.8]  # different domain -> far

    print(f"Python vs Python : {cosine_similarity(python_a, python_b):.2f}  (high)")
    print(f"Python vs Django : {cosine_similarity(python_a, django):.2f}  (medium)")
    print(f"Python vs Redis  : {cosine_similarity(python_a, redis):.2f}  (lower)")
