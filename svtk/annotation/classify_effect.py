#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2017 Matthew Stone <mstone5@mgh.harvard.edu>
# Distributed under terms of the MIT license.

"""
Classify predicted genic effect of SV.
"""


def classify_del(disrupt_dict):
    """
    All deletion hits are DISRUPTING
    """
    regions = list(disrupt_dict.keys())
    if 'exon' in regions:
        return 'LOF'
    if 'UTR' in regions:
        return 'UTR'
    if 'transcript' in regions:
        return 'INTRONIC'
    if 'gene' in regions:
        return 'GENE_OTHER'
    if 'promoter' in regions:
        return 'promoter'

    return 'no_effect'


def classify_dup(disrupt_dict):
    """
    Classify genic effect of a duplication.
    """
    elements = disrupt_dict.keys()
    if 'exon' in elements:
        # duplication internal to exon
        if 'BOTH-INSIDE' in disrupt_dict['exon']:
            return 'LOF'

        # duplication internal to gene, disrupting exon, is LoF
        # duplication spanning gene is copy gain
        # duplication overlapping gene is no effect (one good copy left)
        if 'BOTH-INSIDE' in disrupt_dict['gene']:
            return 'LOF'
        elif 'SPAN' in disrupt_dict['gene']:
            return 'COPY_GAIN'
        else:
            return 'DUP_PARTIAL'

    if 'UTR' in elements:
        if 'BOTH-INSIDE' in disrupt_dict['UTR']:
            return 'UTR'

    if 'transcript' in elements:
        if 'BOTH-INSIDE' in disrupt_dict['transcript']:
            return 'INTRONIC'

    if 'gene' in elements:
        # Hit gene boundary but not transcript/exon, likely due to
        # filtering to canonical transcript
        return 'GENE_OTHER'

    if 'promoter' in elements:
        if 'BOTH-INSIDE' in disrupt_dict['promoter']:
            return 'promoter'

    return 'no_effect'


def classify_inv(disrupt_dict):
    """
    Classify genic effect of a inversion.

    Inversions are disruptive if one or both breakpoints falls within a genic
    element.
    """
    elements = disrupt_dict.keys()
    if 'exon' in elements:
        # breakpoint disrupts exon -> LoF
        if ('BOTH-INSIDE' in disrupt_dict['exon'] or
                'ONE-INSIDE' in disrupt_dict['exon']):
            return 'LOF'

        # if breakpoint spans exon but gene is disrupted -> LoF
        elif ('BOTH-INSIDE' in disrupt_dict['gene'] or
                'ONE-INSIDE' in disrupt_dict['gene']):
            return 'LOF'

        # inversion spanning gene -> no effect
        else:
            return 'INV_SPAN'

    if 'UTR' in elements:
        if ('BOTH-INSIDE' in disrupt_dict['UTR'] or
                'ONE-INSIDE' in disrupt_dict['UTR']):
            return 'UTR'

    if 'transcript' in elements:
        if 'BOTH-INSIDE' in disrupt_dict['transcript']:
            return 'INTRONIC'

    if 'gene' in elements:
        # Hit gene boundary but not transcript/exon, likely due to
        # filtering to canonical transcript
        return 'GENE_OTHER'

    if 'promoter' in elements:
        if ('BOTH-INSIDE' in disrupt_dict['promoter'] or
                'ONE-INSIDE' in disrupt_dict['promoter']):
            return 'promoter'

    return 'no_effect'


def classify_bnd(disrupt_dict):
    """
    Classify genic effect of a breakend.

    An interchromosomal breakpoint falling within a gene is LOF.
    """

    elements = disrupt_dict.keys()

    if 'exon' in elements:
        return 'LOF'
    if 'transcript' in elements:
        return 'LOF'
    if 'gene' in elements:
        return 'GENE_OTHER'
    if 'UTR' in elements:
        return 'UTR'
    if 'promoter' in elements:
        return 'promoter'

    return 'no_effect'


def classify_disrupt(disrupt_dict, svtype):
    """

    Exonic disruptions count as LOF.

    If exonic span or copy gain, check gene:
        gene disruptions count as LOF
        CDS copy_gain/span count as themselves

    If no exonic hit, check UTR:
        UTR disruption counts as UTR

    If no UTR, check promoter:
        disruption counts
    """

    if svtype == 'DEL':
        return classify_del(disrupt_dict)
    if svtype == 'DUP':
        return classify_dup(disrupt_dict)
    if svtype == 'INV':
        return classify_inv(disrupt_dict)
    if svtype == 'BND' or svtype == 'CTX':
        return classify_bnd(disrupt_dict)


def classify_effect(hits):
    hits['element_hit'] = hits['element_type'] + '__' + hits['hit_type']
    effects = hits.groupby('name svtype gene_name'.split())['element_hit']\
                  .agg(lambda s: ','.join(sorted(set(s))))\
                  .reset_index()

    def _apply_classify(row):
        svtype = row.svtype
        element_hit = row.element_hit.split(',')
        element_hit = [h.split('__') for h in element_hit]
        element_hit = {h[0]: h[1] for h in element_hit}

        return classify_disrupt(element_hit, svtype)

    effects['effect'] = effects.apply(_apply_classify, axis=1)

    # only necessary when testing
    effects = effects.drop('element_hit', axis=1)

    return effects