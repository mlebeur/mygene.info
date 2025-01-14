"""
    Mygene.info API v3
    https://mygene.info/v3/
"""

import re
import copy

from biothings.web.settings.default import APP_LIST, ANNOTATION_KWARGS, QUERY_KWARGS

# *****************************************************************************
# Elasticsearch Settings
# *****************************************************************************
# elasticsearch server transport url
ES_HOST = 'localhost:9200'
# elasticsearch index name
ES_INDEX = 'genedoc_mygene_allspecies_current'
# elasticsearch document type
ES_DOC_TYPE = 'gene'

# *****************************************************************************
# Web Application
# *****************************************************************************
API_VERSION = 'v3'
TAX_REDIRECT = "http://t.biothings.io/v1/taxon/{0}?include_children=1"
APP_LIST += [
    (r"/{ver}/species/(\d+)/?", "tornado.web.RedirectHandler", {"url": TAX_REDIRECT}),
    (r"/{ver}/taxon/(\d+)/?", "tornado.web.RedirectHandler", {"url": TAX_REDIRECT}),
    (r"/{ver}/query/?", "web.handlers.MygeneQueryHandler"),
    (r"/{ver}/metadata/?", "web.handlers.MygeneSourceHandler"),
    (r"/metadata/?", "web.handlers.MygeneSourceHandler"),
]

# html header image
HTML_OUT_HEADER_IMG = "/static/favicon.ico"

# for title line on format=html
HTML_OUT_TITLE = """<p style="font-family:'Open Sans',sans-serif;font-weight:bold; font-size:16px;"><a href="http://mygene.info" target="_blank" style="text-decoration: none; color: black">MyGene.info - Gene Annotation as a Service</a></p>"""
METADATA_DOCS_URL = "http://docs.mygene.info/en/latest/doc/data.html"
QUERY_DOCS_URL = "http://docs.mygene.info/en/latest/doc/query_service.html"
ANNOTATION_DOCS_URL = "http://docs.mygene.info/en/latest/doc/annotation_service.html"

# *****************************************************************************
# User Input Control
# *****************************************************************************
DEFAULT_FIELDS = ['name', 'symbol', 'taxid', 'entrezgene']

TAXONOMY = {
    "human": {"tax_id": "9606", "assembly": "hg38"},
    "mouse": {"tax_id": "10090", "assembly": "mm10"},
    "rat": {"tax_id": "10116", "assembly": "rn4"},
    "fruitfly": {"tax_id": "7227", "assembly": "dm3"},
    "nematode": {"tax_id": "6239", "assembly": "ce10"},
    "zebrafish": {"tax_id": "7955", "assembly": "zv9"},
    "thale-cress": {"tax_id": "3702"},
    "frog": {"tax_id": "8364", "assembly": "xenTro3"},
    "pig": {"tax_id": "9823", "assembly": "susScr2"}
}

DATASOURCE_TRANSLATIONS = {
    "refseq:": r"refseq_agg:",
    "accession:": r"accession_agg:",
    "reporter:": r"reporter.\*:",
    "interpro:": r"interpro.id:",
    # GO:xxxxx looks like a ES raw query, so just look for
    # the term as a string in GO's ID (note: searching every keys
    # will raise an error because pubmed key is a int and we're
    # searching with a string term.
    "GO:": r"go.\*.id:go\:",
    # "GO:": r"go.\*:go.",
    "homologene:": r"homologene.id:",
    "reagent:": r"reagent.\*.id:",
    "uniprot:": r"uniprot.\*:",
    "wikipedia:": r"wikipedia.\*:",
    "ensemblgene:": "ensembl.gene:",
    "ensembltranscript:": "ensembl.transcript:",
    "ensemblprotein:": "ensembl.protein:",

    # some specific datasources needs to be case-insentive
    "hgnc:": r"HGNC:",
    "hprd:": r"HPRD:",
    "mim:": r"MIM:",
    "mgi:": r"MGI:",
    "ratmap:": r"RATMAP:",
    "rgd:": r"RGD:",
    "flybase:": r"FLYBASE:",
    "wormbase:": r"WormBase:",
    "tair:": r"TAIR:",
    "zfin:": r"ZFIN:",
    "xenbase:": r"Xenbase:",
    "mirbase:": r"miRBase:",
}

SPECIES_TYPEDEF = {
    'species': {
        'type': list,
        'default': ['all'],
        'strict': False,
        'max': 1000,
        'group': 'esqb',
        'translations': [
            (re.compile(pattern, re.I), translation['tax_id'])
            for (pattern, translation) in TAXONOMY.items()
        ]
    },
    'species_facet_filter': {
        'type': list,
        'default': None,
        'strict': False,
        'max': 1000,
        'group': 'esqb',
        'translations': [
            (re.compile(pattern, re.I), translation['tax_id']) for
            (pattern, translation) in TAXONOMY.items()
        ]
    }
}
FIELD_FILTERS = {
    'entrezonly': {'type': bool, 'default': False, 'group': 'esqb'},
    'ensemblonly': {'type': bool, 'default': False, 'group': 'esqb'},
    'exists': {'type': list, 'default': None, 'max': 1000, 'group': 'esqb', 'strict': False},
    'missing': {'type': list, 'default': None, 'max': 1000, 'group': 'esqb', 'strict': False},
}

DATASOURCE_TRANSLATION_TYPEDEF = [
    (re.compile(pattern, re.I), translation) for
    (pattern, translation) in DATASOURCE_TRANSLATIONS.items()
]
TRIMMED_DATASOURCE_TRANSLATION_TYPEDEF = [
    (re.compile(re.sub(r':.*', '', pattern).replace('\\', '') + '(?!\\.)', re.I),
     re.sub(r':.*', '', translation).replace('\\', ''))
    for(pattern, translation) in DATASOURCE_TRANSLATIONS.items()
]
ANNOTATION_KWARGS = copy.deepcopy(ANNOTATION_KWARGS)
ANNOTATION_KWARGS['*'].update(SPECIES_TYPEDEF)
ANNOTATION_KWARGS['*']['_source']['strict'] = False

QUERY_KWARGS = copy.deepcopy(QUERY_KWARGS)
QUERY_KWARGS['*'].update(SPECIES_TYPEDEF)
QUERY_KWARGS['*'].update(FIELD_FILTERS)
QUERY_KWARGS['*']['_source']['default'] = DEFAULT_FIELDS
QUERY_KWARGS['*']['_source']['strict'] = False
QUERY_KWARGS['GET']['q']['translations'] = DATASOURCE_TRANSLATION_TYPEDEF
QUERY_KWARGS['POST']['scopes']['translations'] = TRIMMED_DATASOURCE_TRANSLATION_TYPEDEF
QUERY_KWARGS['GET']['include_tax_tree'] = {'type': bool, 'default': False, 'group': 'esqb'}
QUERY_KWARGS['POST']['scopes']['default'] = ["_id", "entrezgene", "ensembl.gene", "retired"]
QUERY_KWARGS['POST']['q']['jsoninput'] = True


# *****************************************************************************
# Elasticsearch Query Pipeline
# *****************************************************************************
ES_QUERY_BUILDER = "web.pipeline.MygeneQueryBuilder"
ES_RESULT_TRANSFORM = "web.pipeline.MygeneTransform"
AVAILABLE_FIELDS_EXCLUDED = ['all', 'accession_agg', 'refseq_agg']

# *****************************************************************************
# Analytics Settings
# *****************************************************************************
GA_ACTION_QUERY_GET = 'query_get'
GA_ACTION_QUERY_POST = 'query_post'
GA_ACTION_ANNOTATION_GET = 'gene_get'
GA_ACTION_ANNOTATION_POST = 'gene_post'
GA_TRACKER_URL = 'MyGene.info'

# *****************************************************************************
# Endpoints Specifics & Others
# *****************************************************************************

# kwargs for status check
STATUS_CHECK = {
    'id': '1017',
    'index': 'genedoc_mygene_allspecies_current',
    'doc_type': 'gene'
}

# This essentially bypasses the es.get fallback as in myvariant...
# The first regex matched integers, in which case the query becomes against
# entrezgeneall annotation queries are now multimatch against the following fields
ANNOTATION_ID_REGEX_LIST = [(re.compile(r'^\d+$'), ['entrezgene', 'retired'])]
ANNOTATION_DEFAULT_SCOPES = ["_id", "entrezgene", "ensembl.gene", "retired"]

# for error messages
ID_REQUIRED_MESSAGE = 'Gene ID Required'
ID_NOT_FOUND_TEMPLATE = "Gene ID '{bid}' not found"

# for docs
INCLUDE_DOCS = False
DOCS_STATIC_PATH = 'docs/_build/html'

# url template to redirect for 'include_tax_tree' parameter
INCLUDE_TAX_TREE_REDIRECT_ENDPOINT = 'http://t.biothings.io/v1/taxon'
