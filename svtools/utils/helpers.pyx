#cython: language_level=3
from pysam.libcalignedsegment cimport AlignedSegment
from pysam.libcalignmentfile cimport AlignmentFile

cdef inline int int_max(int a, int b): return a if a >= b else b
cdef inline int int_min(int a, int b): return a if a <= b else b
cdef inline float float_max(float a, float b): return a if a >= b else b
cdef inline float float_min(float a, float b): return a if a <= b else b

cpdef bint is_excluded(AlignedSegment read):
    cdef bint exclude = (read.is_unmapped or
                         read.mate_is_unmapped or
                         read.is_secondary or
                         read.is_duplicate or
                         read.is_supplementary)
    return exclude

cpdef bint is_soft_clipped(AlignedSegment read):
    return (read.cigartuples[0][0] == 4) ^ (read.cigartuples[-1][0] == 4)

cpdef float reciprocal_overlap(int startA, int endA, int startB, int endB):
    """Calculate fraction of reciprocal overlap between two intervals"""

    cdef float fracA = overlap_frac(startA, endA, startB, endB)
    cdef float fracB = overlap_frac(startB, endB, startA, endA)

    cdef float min_frac = float_min(fracA, fracB)
    cdef float recip_overlap = float_max(min_frac, 0)

    return recip_overlap

cpdef float overlap_frac(int startA, int endA, int startB, int endB):
    """Calculate fraction of A overlapped by B"""

    cdef int overlap_start = int_max(startA, startB)
    cdef int overlap_end = int_min(endA, endB)
    
    cdef int overlap_size = overlap_end - overlap_start
    cdef int sizeA = endA - startA
   
    cdef float frac
    if sizeA > 0:
        frac = overlap_size / sizeA
    else:
        frac = 0

    return frac
