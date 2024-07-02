#!/usr/bin/env python3

#################### Import necessary modules ####################
import polars as pl
import pysam
import argparse as ap
from dataclasses import dataclass

#################### Set up argument parser ####################
parser = ap.ArgumentParser(description="""
Script to calculate coverage across regions from a target BED file
""", formatter_class=ap.RawTextHelpFormatter)

parser.add_argument(
    "-a",
    "--alignment-file",
    dest = "alignment",
    type = str,
    help = "Path to alignment file (SAM / BAM)"
)

parser.add_argument(
    "-b",
    "--bed-file",
    dest = "bed",
    type = str,
    help = "Path to bed file"
)

parser.add_argument(
    "-t",
    "--threads",
    dest = "threads",
    type = int,
    default = 2,
    help = "Number of threads to use for parallel processing"
)

args = parser.parse_args()

#################### Create class for coverage object ####################
@dataclass
class CoverageObject:
    """
    Class for calculating coverage across a target BED file

    Args:
        alignment_file (str): Path to alignment file (SAM / BAM)
        bed_file (str): Path to bed file
        threads (int): Number of threads to use for parallel processing
    """
    alignment_file: str
    bed_file: str
    threads: int

    def __post_init__(self):
        self.bed = self.load_bed()
        self.alignment = self.load_alignment()
        self.coverages = self.calculate_region_coverage()


    def load_bed(self) -> pl.DataFrame:
        "Load the bed file as a polars DataFrame"
        # Provide explicit schema for bed file
        dtypes = {"chrom": pl.Utf8, "start":pl.UInt32, "stop":pl.UInt32}

        # Check if provided file is a BED file
        if not self.bed_file.endswith(".bed"):
            raise ValueError("BED file must be in BED format")

        return pl.read_csv(
            source = self.bed_file,
            separator = "\t",
            has_header = True,
            schema_overrides = dtypes
        )

    def load_alignment(self) -> pysam.AlignmentFile:
        "Load the alignment file using pysam"

        # Check if alignment file is in SAM or BAM format and load accordingly
        if self.alignment_file.endswith(".sam"):
            return pysam.AlignmentFile(self.alignment_file, "r", threads = self.threads)

        elif self.alignment_file.endswith(".bam"):
            return pysam.AlignmentFile(self.alignment_file, "rb", threads = self.threads)

        else:
            raise ValueError("Alignment file must be in SAM or BAM format")

    def _calculate_region_coverage(self, chrom:str, start:int, stop:int) -> int:
        """
        Calculate coverage within a specified region

        Args:
            chrom (str): Chromosome
            start (int): Start position of region
            stop (int): Stop position of region

        Returns:
            int: Coverage (reads covering) of specified region
        """
        try:
            return self.alignment.count(contig = chrom, start = start, stop = stop)
        except:
            return 0

    def calculate_region_coverage(self) -> dict:
        "Function to iterate through the bed file regions and return coverages"
        coverages = {} # dict to store coverages; {(chrom, start, stop): coverage}

        # Iterate through bed file (polars dataframe)
        for row in self.bed.rows(named=True):
            chrom = row["chrom"]
            start = row["start"]
            stop = row["end"]

            # use pysam count function to calculate coverage and store (AlignmentFile method)
            coverages[(chrom, start, stop)] = self._calculate_region_coverage(chrom, start, stop)

        return coverages

#################### Main script ####################
cov = CoverageObject(
    alignment_file = args.alignment,
    bed_file = args.bed,
    threads = args.threads
)

# Neatly print out coverages
for k in cov.coverages:
    print(f"Chromosome {k[0]}: {cov.coverages[k]:,}")
