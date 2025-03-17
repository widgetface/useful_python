from utils.sequence_utils import (
    count_k_mers,
    count_nucleotides,
    find_longest_dna_palindrome,
    update_k_mer_counts,
    update_nucleotide_counts,
    validate_sequence,
)

import pytest

INVALID_SEQUENCE = "A"
SEQUENCE = "ATGTGCTTGC"
PALINDROME = "TGAATTCGGC"
INVALID_PALINDROME = "GCAACGTAGCTGG"
NUCLEOTIDE_LIST = {"A", "T", "G", "C"}


# Run test ith  python -m pytest tests
@pytest.mark.count_kemers
def test_count_kmers():
    valid_kmer_2 = {"at": 1, "tg": 3, "gt": 1, "gc": 2, "ct": 1, "tt": 1}
    valid_kmer_3 = {
        "atg": 1,
        "tgt": 1,
        "gtg": 1,
        "tgc": 2,
        "gct": 1,
        "ctt": 1,
        "ttg": 1,
    }
    valid_kmer_4 = {
        "atgt": 1,
        "tgtg": 1,
        "gtgc": 1,
        "tgct": 1,
        "gctt": 1,
        "cttg": 1,
        "ttgc": 1,
    }

    valid_kmer_5 = {
        "atgtg": 1,
        "tgtgc": 1,
        "gtgct": 1,
        "tgctt": 1,
        "gcttg": 1,
        "cttgc": 1,
    }

    assert count_k_mers(sequence=INVALID_SEQUENCE, number_nucleotides=2) == {}
    assert count_k_mers(sequence=SEQUENCE, number_nucleotides=2) == valid_kmer_2
    assert count_k_mers(sequence=SEQUENCE, number_nucleotides=3) == valid_kmer_3
    assert count_k_mers(sequence=SEQUENCE, number_nucleotides=4) == valid_kmer_4
    assert count_k_mers(sequence=SEQUENCE, number_nucleotides=5) == valid_kmer_5


@pytest.mark.count_nucleotides
def test_count_nucleotides():
    valid_count = {"a": 1, "t": 4, "g": 3, "c": 2}
    assert count_nucleotides(SEQUENCE) == valid_count


@pytest.mark.find_longest_palindrome
def test_find_longest_palidrome():
    longest_palidrome = find_longest_dna_palindrome(PALINDROME, min_length=6)
    invalid_longest_palindrome = find_longest_dna_palindrome(
        INVALID_PALINDROME, min_length=6
    )
    assert invalid_longest_palindrome["palindrome_seq"] == ""
    assert invalid_longest_palindrome["palindrome_length"] == 0
    assert longest_palidrome["palindrome_seq"] == "GAATTC"
    assert longest_palidrome["palindrome_length"] == 6


@pytest.mark.update_k_mer_counts
def test_update_k_mer_counts():
    current_kmer_count = {
        "atg": 1,
        "tgt": 1,
        "gtg": 1,
        "tgc": 2,
        "gct": 1,
        "ctt": 1,
        "ttg": 1,
    }
    new_ker_count = {
        "atg": 1,
        "tgt": 2,
        "gtg": 1,
        "tgc": 2,
        "gct": 1,
        "ctt": 1,
        "ttg": 1,
    }

    valid_result = {
        "atg": 2,
        "tgt": 3,
        "gtg": 2,
        "tgc": 4,
        "gct": 2,
        "ctt": 2,
        "ttg": 2,
    }

    assert update_k_mer_counts(current_kmer_count, {}) == current_kmer_count
    assert update_k_mer_counts(current_kmer_count, new_ker_count) == valid_result


@pytest.mark.update_nucleotide_counts
def test_update_nucleotide_counts():
    current_count = {
        "meta_data": {
            "adenine_count": 1,
            "thymine_count": 1,
            "guanine_count": 1,
            "cytosine_count": 1,
        }
    }

    new_count = {"a": 2, "t": 3, "g": 1, "c": 5}

    valid_count = {
        "meta_data": {
            "adenine_count": 3,
            "thymine_count": 4,
            "guanine_count": 2,
            "cytosine_count": 6,
        }
    }
    assert update_nucleotide_counts({}, current_count) == current_count
    assert update_nucleotide_counts(new_count, current_count) == valid_count


@pytest.mark.validate_sequence
def test_validate_sequence():
    assert (
        validate_sequence(sequence="AGCTGGCCTTATTATT", letter_list=NUCLEOTIDE_LIST)
        is True
    )
    assert (
        validate_sequence(sequence="OGCTGGCCTTATTATT", letter_list=NUCLEOTIDE_LIST)
        is False
    )
