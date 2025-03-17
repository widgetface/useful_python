import json
import os
from typing import List, TypedDict
from multiprocessing import Manager, Pool

# from typing import Dict, List, NamedTuple, Set, TypedDict
# from collections import defaultdict, Counter
# from dataclasses import dataclass, field
from functools import partial
import time
from utils.sequence_utils import (
    count_k_mers,
    count_nucleotides,
    create_dna_sequence_record,
    update_k_mer_counts,
    update_nucleotide_counts,
    validate_sequence,
)

from utils.data_types import DNASequence, SequenceStatistics


NUCLEOTIDE_LIST = {"A", "T", "G", "C"}
PALINDROME_MIN_LENGTH = 20
INDEX = 0
FILE_PATH = "./data/dna_sequences.json"
# The sequence analaysis is a CPU bound task:
# For CPU-bound tasks: Start with num_cores = os.cpu_count().
# This usually provides good performance, but you may want to experiment with
#  using num_cores // 2 or even num_cores - 1 to reduce the load on the system.
# // 2: This takes the result from os.cpu_count() and divides it by 2, while discarding any
# remainder (it floors the division to the nearest integer).
num_cores = os.cpu_count() // 2


class DNASequenceData(TypedDict):
    num_sequences: int
    sequence_length: int
    sequences: List[str]


def initialise_sequence_statistics() -> SequenceStatistics:
    seq_stats = {
        "total_adenine_count": 0,
        "total_thymine_count": 0,
        "total_guanine_count": 0,
        "total_cytosine_count": 0,
        "total_sequences_count": 0,
        "invalid_sequences_count": 0,
        "k_mer_count_2": {},
        "k_mer_count_3": {},
        "k_mer_count_4": {},
        "k_mer_count_5": {},
        "dna_sequences": [],
    }
    return seq_stats


def load_sequences_file(file_path: str) -> DNASequenceData:
    with open(file_path) as f:
        data = json.load(f)
        return data


def calculate_dna_sequence_statistics(sequences: List[str]) -> SequenceStatistics:
    sequences_stats = SequenceStatistics()
    append_seq = sequences_stats.dna_sequences.append

    for index, sequence in enumerate(sequences):
        nucleotide_counts = count_nucleotides(sequence=sequence)
        sequences_stats = update_nucleotide_counts(
            nucleotide_counts=nucleotide_counts, sequence_stats=sequences_stats
        )

        k_mers_2 = count_k_mers(sequence=sequence, number_nucleotides=2)

        k_mers_3 = count_k_mers(sequence=sequence, number_nucleotides=3)

        k_mers_4 = count_k_mers(sequence=sequence, number_nucleotides=4)

        k_mers_5 = count_k_mers(sequence=sequence, number_nucleotides=5)

        sequences_stats.k_mer_count_2 = update_k_mer_counts(
            sequences_stats.k_mer_count_2, k_mers_2
        )

        sequences_stats.k_mer_count_3 = update_k_mer_counts(
            sequences_stats.k_mer_count_2, k_mers_3
        )

        sequences_stats.k_mer_count_4 = update_k_mer_counts(
            sequences_stats.k_mer_count_4, k_mers_4
        )
        sequences_stats.k_mer_count_5 = update_k_mer_counts(
            sequences_stats.k_mer_count_5, k_mers_5
        )

        dna_sequence = create_dna_sequence_record(
            id=index,
            nucleotide_counts=nucleotide_counts,
            sequence=sequence,
            min_length=PALINDROME_MIN_LENGTH,
        )
        # This does significantly save time 55 sec with
        # sequences_stats.dna_sequences.append
        # 51 sec with append_seq
        append_seq(dna_sequence)

    return sequences_stats

    # Example task function


def process_data(sequence: str):
    nucleotide_counts = count_nucleotides(sequence=sequence)
    k_mers = {}

    k_mers["k_mer_n2_count"] = count_k_mers(sequence=sequence, number_nucleotides=2)

    k_mers["k_mer_n3_count"] = count_k_mers(sequence=sequence, number_nucleotides=3)

    k_mers["k_mer_n4_count"] = count_k_mers(sequence=sequence, number_nucleotides=4)

    k_mers["k_mer_n5_count"] = count_k_mers(sequence=sequence, number_nucleotides=5)

    return create_dna_sequence_record(
        id=INDEX + 1,
        nucleotide_counts=nucleotide_counts,
        sequence=sequence,
        min_length=PALINDROME_MIN_LENGTH,
        k_mers=k_mers,
    )

    # Function to run multiprocessing


def process_data_parallel(data):
    with Pool(processes=num_cores) as pool:
        results = pool.map(process_data, data)
    return results


def process_sequence_statistics(
    data: List[DNASequence], total_count: int, invalid_count: int
) -> SequenceStatistics:
    seq_doc = initialise_sequence_statistics()
    print(f"SEQ DOC = {seq_doc}")
    seq_doc["total_sequences_count"] = total_count
    seq_doc["invalid_sequences_count"] = invalid_count
    # "total_adenine_count": 0,
    # "total_thymine_count": 0,
    # "total_guanine_count": 0,
    # "total_cytosine_count": 0,
    # "total_sequences": 0,
    # "invalid_sequences": 0,
    # "k_mer_count_2": {},
    # "k_mer_count_3": {},
    # "k_mer_count_4": {},
    # "k_mer_count_5":
    # ///
    #         adenine_count: int
    # thymine_count: int
    # guanine_count: int
    # cytosine_count: int
    # palindrome: Palindrome
    # motifs: Dict[str, int]
    # k_mers: K_MERS
    for item in data:
        seq_doc["total_adenine_count"] += item.adenine_count
        seq_doc["total_thymine_count"] += item.thymine_count
        seq_doc["total_guanine_count"] += item.guanine_count
        seq_doc["total_cytosine_count"] += item.cytosine_count
        seq_doc["dna_sequences"].append(item)
    return seq_doc


if __name__ == "__main__":
    sequence_data = load_sequences_file(FILE_PATH)
    validate_partial = partial(
        validate_sequence, letter_list=NUCLEOTIDE_LIST, min_length=2
    )
    validate = validate_partial
    cleaned_sequence_data = [
        seq for seq in sequence_data["sequences"] if validate(sequence=seq)
    ]

    total_count = sequence_data["num_sequences"]
    invalid_count = total_count - len(cleaned_sequence_data)

    # Using multiprocessing
    start_time = time.time()
    results = process_data_parallel(cleaned_sequence_data)

    seq_statistics = process_sequence_statistics(
        data=results, total_count=total_count, invalid_count=invalid_count
    )

    print(seq_statistics)
    print("Results using multiprocessing:", results[0])
    print("Time taken using multiprocessing:", time.time() - start_time)
