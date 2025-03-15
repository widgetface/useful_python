import json
from multiprocessing import Pool
from typing import Dict, List, NamedTuple, TypedDict, Tuple, Set
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from functools import partial
import time

FILE_PATH = "./data/dna_sequences.json"
GC_ISLAND_MOTIF = "CG"
TATA_BOX_MOTIF = "TATA"
MIN_PALINDROME_LENGTH = 20
NUCLEOTIDE_LIST = {"A", "T", "G", "C"}


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


def validate_sequence(
    sequence: List[str], letter_list: Set[str], min_length=2
) -> List[str]:
    clean_list = []
    # Check if sequence is long enough and contains only valid letters
    if len(sequence) > min_length and all(letter in letter_list for letter in sequence):
        if sequence not in clean_list:
            clean_list.append(sequence)
            return True
    else:
        return False


def find_motif(sequence: str, motif: str) -> List[str]:
    return [
        i for i in range(len(sequence) - 1) if sequence[i : i + len(motif)] == motif
    ]


# is_palindrome = lambda x: x == x[::-1]


# def find_longest_palindrome(sequence: str, min_length: int) -> Palindrome:
#     last = len(sequence)
#     lst = {"palindrome_seq": "", "palindrome_length": 0}
#     for i in range(last):
#         for j in range(i + 1, last):
#             b = sequence[i : j + 1]
#             a = is_palindrome(b) if len(b) > min_length else False
#             if a and lst["palindrome_length"] < len(b):
#                 lst["palindrome_seq"] = b
#                 lst["palindrome_length"] = len(b)
#     return lst


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


# res = longest_palindrome("GAGTABBACT", 3)


def create_markdown_report(data):
    #     Python ljust() method is used to left-justify a string, padding it with a specified character (space by default) to reach a desired width. This method is particularly useful when we want to align text in a consistent format,
    #  such as in tables or formatted outputs.
    # Here’s a basic example of how to use ljust() method:
    # s1 = "Hello"
    # s2 = s1.ljust(10)
    # print(s2)
    pass


def count_nucleotides(sequence: str) -> NucleotideCount:
    return defaultdict(int, Counter(sequence.lower().strip()))


def count_k_mers(sequence, number_nucleotides) -> Dict[str, int]:
    oligo_counts = defaultdict(int)
    sequence.lower().strip()
    for i, _ in enumerate(sequence[: -(number_nucleotides - 1)]):
        key = sequence[i : i + number_nucleotides]
        oligo_counts[key] += 1
    return oligo_counts


def update_k_mer_counts(current_counts: dict, new_counts: dict) -> Dict:
    current_counts = Counter(current_counts)
    current_counts.update(new_counts)
    return dict(current_counts)


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
    # tata_boxes = find_motif(sequence=sequence, motif=TATA_BOX_MOTIF)
    return DNASequence(
        id=id,
        adenine_count=nucleotide_counts["a"],
        thymine_count=nucleotide_counts["t"],
        guanine_count=nucleotide_counts["g"],
        cytosine_count=nucleotide_counts["c"],
        palindrome=longest_palindrome,
        motifs={"cpg_islands": cpg_islands},
    )


def calculate_dna_sequence_statistics(index_seq: Tuple[int, str]) -> SequenceStatistics:
    index, sequence = index_seq
    sequences_stats = SequenceStatistics()

    # for index, sequence in enumerate(sequences):
    #     print(index)
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
    sequences_stats.dna_sequences.append(dna_sequence)

    return sequences_stats


def calculate_dna_sequence_statistics2(sequences: List[str]) -> SequenceStatistics:
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


if __name__ == "__main__":
    sequence_data = load_sequences_file(FILE_PATH)
    start_time = time.time()
    # While this is quicker the effect is marginal but worth
    #  thinking about for very large datasets
    validate_partial = partial(
        validate_sequence, letter_list=NUCLEOTIDE_LIST, min_length=2
    )
    validate = validate_partial
    cleaned_sequence_data = [seq for seq in sequence_data if validate(sequence=seq)]
    print("Time taken using multiprocessing:", time.time() - start_time)
    print(len(cleaned_sequence_data))
    start_time = time.time()
    dna_statistics = calculate_dna_sequence_statistics2(cleaned_sequence_data)
    # Belo is about a second faster.
    # get_stats = calculate_dna_sequence_statistics
    # dna_statistics = [
    #     get_stats(index_seq) for index_seq in enumerate(cleaned_sequence_data)
    # ]
    # print(dna_statistics)
    print("Time taken using multiprocessing:", time.time() - start_time)
