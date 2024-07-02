#!/usr/bin/env python3

# Load the module form the relative path
import sys
import pysam
import polars
sys.path.append("../..")
from src.python.calc_target_coverage import CoverageObject


def test_alignment_file_loading():
    cov = CoverageObject(
            alignment_file = "../../NA12878.mapped.ILLUMINA.bwa.CEU.low_coverage.20121211.sub.bam",
            bed_file = "../../chromosomes.bed",
            threads = 2
    )

    assert type(cov.alignment) == pysam.AlignmentFile

def test_bed_file_loading():
    cov = CoverageObject(
            alignment_file = "../../NA12878.mapped.ILLUMINA.bwa.CEU.low_coverage.20121211.sub.bam",
            bed_file = "../../chromosomes.bed",
            threads = 2
    )

    assert cov.bed.is_empty() == False


def test_coverage_calculation():
    cov = CoverageObject(
                alignment_file = "../../NA12878.mapped.ILLUMINA.bwa.CEU.low_coverage.20121211.sub.bam",
                bed_file = "../../chromosomes.bed",
                threads = 2
    )

    assert len(cov.coverages) == 24
