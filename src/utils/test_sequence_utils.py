from typing import Dict, List, Set
from collections import defaultdict, Counter
from .data_types import (
    DNASequence,
    K_MERS,
    NucleotideCount,
    NucleotideCounts,
    SequenceStatistics,
)
from .markdown import MarkdownGenerator

GC_ISLAND_MOTIF = "CG"
TATA_BOX_MOTIF = "TATA"
MIN_PALINDROME_LENGTH = 20


def find_top_values(results: K_MERS, limit: int) -> List[tuple]:
    return sorted(results.items(), key=lambda item: item[1], reverse=True)[:limit]


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
    positions = [
        i for i in range(len(sequence) - 1) if sequence[i : i + len(motif)] == motif
    ]
    step = len(motif)
    pos_len = len(positions)
    longest = 0
    seen = set()
    for i in range(0, pos_len, step):
        value = sequence[i : i + step]
        if value == motif:
            longest += step
        else:
            seen.add(longest)
            longest = 0
    return max(seen) if len(seen) > 0 else 0


def reverse_complement(seq):
    """Returns the reverse complement of a DNA sequence."""
    complement = {"A": "T", "T": "A", "C": "G", "G": "C"}
    return "".join(complement[base] for base in reversed(seq))


def precompute_reverse_complement(sequence):
    """Precomputes the reverse complement for a DNA sequence."""
    return reverse_complement(sequence)


def find_longest_dna_palindrome(sequence, min_length=20):
    """Finds all palindromes in a DNA sequence of at least min_length using precomputed reverse complement."""
    longest = {"palindrome_seq": "", "palindrome_length": 0}
    seq_length = len(sequence)

    # Precompute the reverse complement of the entire sequence
    rev_complement = precompute_reverse_complement(sequence)

    # Loop over all possible subsequences starting from min_length up to the sequence length
    for length in range(min_length, seq_length + 1):
        for i in range(seq_length - length + 1):
            subseq = sequence[i : i + length]
            rev_subseq = rev_complement[
                seq_length - i - length : seq_length - i
            ]  # Get the reverse complement slice
            if subseq == rev_subseq and len(subseq) > longest["palindrome_length"]:
                longest["palindrome_seq"] = subseq
                longest["palindrome_length"] = len(subseq)

    return longest


def count_nucleotides(sequence: str) -> NucleotideCount:
    return defaultdict(int, Counter(sequence.lower().strip()))


def update_nucleotide_counts(
    nucleotide_counts: NucleotideCounts, sequence_stats: SequenceStatistics
) -> SequenceStatistics:
    sequence_stats["meta_data"]["adenine_count"] += nucleotide_counts.get("a", 0)
    sequence_stats["meta_data"]["thymine_count"] += nucleotide_counts.get("t", 0)
    sequence_stats["meta_data"]["guanine_count"] += nucleotide_counts.get("g", 0)
    sequence_stats["meta_data"]["cytosine_count"] += nucleotide_counts.get("c", 0)
    return sequence_stats


def create_dna_sequence_record(
    id: int,
    nucleotide_counts: NucleotideCounts,
    sequence: str,
    min_length: int,
    k_mers: K_MERS,
) -> DNASequence:
    longest_palindrome = find_longest_dna_palindrome(
        sequence=sequence, min_length=min_length
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
        k_mers=k_mers,
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
    return dict(
        sorted(oligo_counts.items(), key=lambda item: item[1], reverse=True)[:5]
    )


def update_k_mer_counts(current_counts: dict, new_counts: dict) -> Dict:
    current_counts = Counter(current_counts)
    current_counts.update(new_counts)
    return dict(current_counts)


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


def create_k_mer_row(header: List[str], kmers: List[tuple]) -> List[List[str]]:
    rows = []
    rows.append(header)
    for k_mer in kmers:
        key, value = k_mer
        rows.append([key, str(value)])
    return rows


def generate_report(sequence_stats: SequenceStatistics, output_path: str):
    md = MarkdownGenerator()
    md.add_header("DNA Statistics Report")
    md.add_linebreak()
    md.add_text(f"Total number sequences = {sequence_stats['total_sequences_count']}")
    md.add_text(
        f"Total number invalid sequences = {sequence_stats['invalid_sequences_count']}"
    )
    md.add_linebreak()
    md.add_text("Total nucleotide counts:")
    md.add_linebreak()
    md.add_text(f"Adenine = {sequence_stats['total_adenine_count']}")
    md.add_text(f"Thymine = {sequence_stats['total_thymine_count']}")
    md.add_text(f"Guanine = {sequence_stats['total_guanine_count']}")
    md.add_text(f"Cytosine = {sequence_stats['total_cytosine_count']}")
    md.add_linebreak()
    kmers_2_rows = create_k_mer_row(
        header=["k_mer (k2)", "number"], kmers=sequence_stats["total_k_mer_count_2"]
    )
    md.add_table(kmers_2_rows)
    kmers_3_rows = create_k_mer_row(
        header=["k_mer (k3)", "number"], kmers=sequence_stats["total_k_mer_count_3"]
    )
    md.add_table(kmers_3_rows)
    md.save(output_path)
