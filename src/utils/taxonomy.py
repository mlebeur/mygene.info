from pyes import ES
from pyes.exceptions import NotFoundException

from config import ES_HOST


class TaxonomyQuery:
    def __init__(self):
        self.es = ES(ES_HOST)
        self._index = 'taxonomy'
        self._doc_type = 'species'

    def get_species_info(self, taxid, include_children=False):
        taxid = int(taxid)
        try:
            res = self.es.get(self._index, self._doc_type, taxid)
        except NotFoundException:
            res = None
        if res:
            if include_children:
                res['children'] = self.get_all_children_tax_ids(taxid, include_self=False)
            return res

    def get_all_children_tax_ids(self, taxid, has_gene=True, include_self=True, raw=False):

        # q = {
        #     "query": {
        #         "term": {
        #             "lineage": taxid
        #         }
        #     }
        # }
        # if has_gene is not None:
        #     q['query']['term']['has_gene'] = bool(has_gene)

        q = {
            'query': {
                "query_string": {}
            }
        }
        if has_gene:
            q['query']['query_string']['query'] = "lineage:{} AND has_gene:true".format(taxid)
        else:
            q['query']['query_string']['query'] = "lineage:{}".format(taxid)

        res = self.es.search_raw(q, indices=self._index, doc_types=self._doc_type, fields='_id', size=1000)
        if raw:
            return res
        taxid_li = [int(x['_id']) for x in res['hits']['hits']]
        if include_self:
            if taxid not in taxid_li:
                taxid_li.append(taxid)
        elif taxid in taxid_li:
            taxid_li.remove(taxid)

        return sorted(taxid_li)

    def get_expanded_species_li(self, taxid_li, max=1000):
        taxid_set = set()
        for taxid in taxid_li:
            taxid_set |= set(self.get_all_children_tax_ids(taxid))
            if len(taxid_set) >= max:
                break
        return sorted(taxid_set)[:max]
        # if len(taxid_set) > max:
        #     out = {"truncated": True, "list": sorted(taxid_set)[:max]}
        # else:
        #     out = sorted(taxid_set)
        # return out
