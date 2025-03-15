import json
import os
from multiprocessing import Manager, Pool
from typing import Dict, List, NamedTuple, Set, TypedDict
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from functools import partial
import time


FILE_PATH = "./data/dna_sequences.json"
GC_ISLAND_MOTIF = "CG"
TATA_BOX_MOTIF = "TATA"
MIN_PALINDROME_LENGTH = 20
NUCLEOTIDE_LIST = {"A", "T", "G", "C"}
INDEX = 0
# The sequence analaysis is a CPU bound task:
# For CPU-bound tasks: Start with num_cores = os.cpu_count().
# This usually provides good performance, but you may want to experiment with
#  using num_cores // 2 or even num_cores - 1 to reduce the load on the system.
# // 2: This takes the result from os.cpu_count() and divides it by 2, while discarding any
# remainder (it floors the division to the nearest integer).
num_cores = os.cpu_count() // 2


class NucleotideCount(TypedDict):
    a: int
    t: int
    g: int
    c: int


class NucleotideCounts(TypedDict):
    a: int
    b: int
    c: int
    d: int


class Palindrome(NamedTuple):
    sequence: str
    longest: int


class DNASequence(NamedTuple):
    id: int
    adenine_count: int
    thymine_count: int
    guanine_count: int
    cytosine_count: int
    palindrome: Palindrome
    motifs: Dict[str, int]


class TestNC(TypedDict):
    adenine_count: int = 0
    thymine_count: int = 0
    guanine_count: int = 0
    cytosine_count: int = 0


@dataclass(slots=True)
class SequenceStatistics:
    adenine_count: int = 0
    thymine_count: int = 0
    guanine_count: int = 0
    cytosine_count: int = 0
    k_mer_count_2: Dict[str, int] = field(default_factory=dict)
    k_mer_count_3: Dict[str, int] = field(default_factory=dict)
    k_mer_count_4: Dict[str, int] = field(default_factory=dict)
    k_mer_count_5: Dict[str, int] = field(default_factory=dict)
    dna_sequences: List[DNASequence] = field(default_factory=list)


class MetaData(TypedDict):
    total_adenine_count: int
    total_thymine_count: int
    total_guanine_count: int
    total_cytosine_count: int
    k_mer_count_2: Dict[str, int]
    k_mer_count_3: Dict[str, int]
    k_mer_count_4: Dict[str, int]
    k_mer_count_5: Dict[str, int]


class SequenceStatisticsTest(TypedDict):
    meta_data: MetaData
    dna_sequences: List[DNASequence] = {}


def clean_sequence_data(
    sequences: List[str], letter_list=None, min_length=2
) -> List[str]:
    if letter_list is None:
        letter_list = {"A", "T", "G", "C"}
    else:
        letter_list = set(letter_list)
    clean_list = []
    for sequence in sequences:
        # Check if sequence is long enough and contains only valid letters
        if len(sequence) > min_length and all(
            letter in letter_list for letter in sequence
        ):
            # Add to clean_list if not seen before
            if sequence not in clean_list:
                clean_list.append(sequence)

    return clean_list


def find_motif(sequence: str, motif: str) -> List[str]:
    return [
        i for i in range(len(sequence) - 1) if sequence[i : i + len(motif)] == motif
    ]


def find_longest_palindrome(sequence: str, min_length: int):
    # Function to expand around a center to find a palindrome
    def expand_around_center(left, right):
        while left >= 0 and right < len(sequence) and sequence[left] == sequence[right]:
            left -= 1
            right += 1

        return sequence[left + 1 : right]

    longest_palindrome = {"palindrome_seq": "", "palindrome_length": 0}

    for i in range(len(sequence)):
        # Check for odd-length palindromes (center is a single character)
        odd_palindrome = expand_around_center(i, i)
        # Check for even-length palindromes (center is between two characters)
        even_palindrome = expand_around_center(i, i + 1)

        # Update the longest palindrome found (odd length check)
        if (
            len(odd_palindrome) >= min_length
            and len(odd_palindrome) > longest_palindrome["palindrome_length"]
        ):
            longest_palindrome["palindrome_seq"] = odd_palindrome
            longest_palindrome["palindrome_length"] = len(odd_palindrome)

        # Update the longest palindrome found (even length check)
        if (
            len(even_palindrome) >= min_length
            and len(even_palindrome) > longest_palindrome["palindrome_length"]
        ):
            longest_palindrome["palindrome_seq"] = even_palindrome
            longest_palindrome["palindrome_length"] = len(even_palindrome)

    return longest_palindrome


def count_nucleotides(sequence: str) -> NucleotideCount:
    return defaultdict(int, Counter(sequence.lower().strip()))


def load_sequences_file(file_path: str) -> List[str]:
    with open(file_path) as f:
        data = json.load(f)
        return data["sequences"]


def update_nucleotide_counts(
    nucleotide_counts: NucleotideCounts, sequence_stats: SequenceStatistics
) -> SequenceStatistics:
    sequence_stats.adenine_count += nucleotide_counts["a"]
    sequence_stats.thymine_count += nucleotide_counts["t"]
    sequence_stats.guanine_count += nucleotide_counts["g"]
    sequence_stats.cytosine_count += nucleotide_counts["c"]
    return sequence_stats


def create_dna_sequence_record(
    id: int, nucleotide_counts: NucleotideCounts, sequence: str
) -> DNASequence:
    longest_palindrome = find_longest_palindrome(
        sequence=sequence, min_length=MIN_PALINDROME_LENGTH
    )
    cpg_islands = find_motif(sequence=sequence, motif=GC_ISLAND_MOTIF)
    tata_boxes = find_motif(sequence=sequence, motif=TATA_BOX_MOTIF)

    return DNASequence(
        id=id,
        adenine_count=nucleotide_counts["a"],
        thymine_count=nucleotide_counts["t"],
        guanine_count=nucleotide_counts["g"],
        cytosine_count=nucleotide_counts["c"],
        palindrome=longest_palindrome,
        motifs={"cpg_islands": cpg_islands, "tata_boxes": tata_boxes},
    )


def count_k_mers(sequence, number_nucleotides) -> Dict[str, int]:
    oligo_counts = defaultdict(int)
    sequence = sequence.lower().strip()
    sequence_length = len(sequence)
    if sequence_length < number_nucleotides:
        return {}
    for i, _ in enumerate(sequence[: -(number_nucleotides - 1)]):
        key = sequence[i : i + number_nucleotides]
        oligo_counts[key] += 1
    return oligo_counts


def update_k_mer_counts(current_counts: dict, new_counts: dict) -> Dict:
    current_counts = Counter(current_counts)
    current_counts.update(new_counts)
    return dict(current_counts)


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
            id=index, nucleotide_counts=nucleotide_counts, sequence=sequence
        )
        # This does significantly save time 55 sec with
        # sequences_stats.dna_sequences.append
        # 51 sec with append_seq
        append_seq(dna_sequence)

    return sequences_stats


def validate_sequence(
    sequence: List[str], letter_list: Set[str], min_length=2
) -> List[str]:
    seen_list = []
    seen = seen_list.append
    # Check if sequence is long enough and contains only valid letters
    if len(sequence) > min_length and all(letter in letter_list for letter in sequence):
        if sequence not in seen_list:
            seen(sequence)
            return True
    else:
        return False


if __name__ == "__main__":
    sequence_data = load_sequences_file(FILE_PATH)
    validate_partial = partial(
        validate_sequence, letter_list=NUCLEOTIDE_LIST, min_length=2
    )
    validate = validate_partial
    cleaned_sequence_data = [seq for seq in sequence_data if validate(sequence=seq)]

    # print(len(cleaned_sequence_data))
    # Example task function
    def process_data(sequence: str, seq_doc: SequenceStatisticsTest):
        print(f"nuc coubt {seq_doc}")
        nucleotide_counts = count_nucleotides(sequence=sequence)
        print(nucleotide_counts)
        dna_sequence = create_dna_sequence_record(
            id=INDEX + 1, nucleotide_counts=nucleotide_counts, sequence=sequence
        )

        return dna_sequence

    # Function to run multiprocessing
    def process_data_parallel(data):
        print("Start")
        seq_doc = SequenceStatisticsTest()
        with Manager() as manager:
            # Create a dictionary to store the running total
            nucleotide_totals = manager.dict(seq_doc)
            print("Done manager")
            # Create a pool of processes
            with Pool(processes=num_cores) as pool:
                print("Start pool")
                results = pool.starmap(process_data, [(seq, seq_doc) for seq in data])
        return results

    # Using multiprocessing
    start_time = time.time()
    results_parallel = process_data_parallel(cleaned_sequence_data)
    print("Results using multiprocessing:", results_parallel)
    print("Time taken using multiprocessing:", time.time() - start_time)
