"""Duplicate detection using Ratcliff-Obershelp similarity algorithm."""

from __future__ import annotations

import re
from typing import NamedTuple

from github_pipeline_triage.core.types import DuplicatePair, Issue


class Match(NamedTuple):
    i: int
    j: int
    size: int


def build_b2j(b: str) -> dict[str, list[int]]:
    b2j: dict[str, list[int]] = {}
    for j, ch in enumerate(b):
        if ch in b2j:
            b2j[ch].append(j)
        else:
            b2j[ch] = [j]
    return b2j


def find_longest_match(
    a: str,
    b: str,
    alo: int,
    ahi: int,
    blo: int,
    bhi: int,
    b2j: dict[str, list[int]],
) -> Match:
    best_i = alo
    best_j = blo
    best_size = 0
    j2len: dict[int, int] = {}

    for i in range(alo, ahi):
        new_j2len: dict[int, int] = {}
        js = b2j.get(a[i], [])
        for j in js:
            if j < blo:
                continue
            if j >= bhi:
                break
            k = j2len.get(j - 1, 0) + 1
            new_j2len[j] = k
            if k > best_size:
                best_i = i - k + 1
                best_j = j - k + 1
                best_size = k
        j2len = new_j2len

    while best_i > alo and best_j > blo and a[best_i - 1] == b[best_j - 1]:
        best_i -= 1
        best_j -= 1
        best_size += 1

    while (
        best_i + best_size < ahi
        and best_j + best_size < bhi
        and a[best_i + best_size] == b[best_j + best_size]
    ):
        best_size += 1

    return Match(best_i, best_j, best_size)


def similarity_ratio(a: str, b: str) -> float:
    if len(a) == 0 and len(b) == 0:
        return 1.0
    b2j = build_b2j(b)
    total_matches = 0
    queue: list[tuple[int, int, int, int]] = [(0, len(a), 0, len(b))]

    while queue:
        alo, ahi, blo, bhi = queue.pop()
        m = find_longest_match(a, b, alo, ahi, blo, bhi, b2j)
        if m.size == 0:
            continue
        total_matches += m.size
        if alo < m.i and blo < m.j:
            queue.append((alo, m.i, blo, m.j))
        if m.i + m.size < ahi and m.j + m.size < bhi:
            queue.append((m.i + m.size, ahi, m.j + m.size, bhi))

    return (2 * total_matches) / (len(a) + len(b))


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", title.lower())


def find_duplicates(issues: list[Issue]) -> list[DuplicatePair]:
    opens = [i for i in issues if i.state.value == "OPEN"]
    normed = [(i, normalize_title(i.title)) for i in opens]
    dupes: list[DuplicatePair] = []

    for idx, (issue_i, normed_i) in enumerate(normed):
        for j in range(idx + 1, len(normed)):
            issue_j, normed_j = normed[j]
            ratio = similarity_ratio(normed_i, normed_j)
            if ratio > 0.85:
                dupes.append(
                    DuplicatePair(
                        a=issue_i.number,
                        b=issue_j.number,
                        similarity=round(ratio, 4),
                    )
                )

    return dupes
