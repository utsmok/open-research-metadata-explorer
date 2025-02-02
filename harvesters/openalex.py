import pyalex
from collections import defaultdict
from itertools import batched, chain
from pyalex import (
    Work,
    Works,
    Author,
    Authors,
    Source,
    Sources,
    Publisher,
    Publishers,
    Institution,
    Institutions,
    Funder,
    Funders,
    Topic,
    Topics,
    Subfield,
    Subfields,
    Field,
    Fields,
    Domain,
    Domains,
)
from pyalex.api import BaseOpenAlex
from harvesters.generics import Harvester, SearchEntityType, QueryValueType
from settings import SETTINGS

class OpenAlexHarvester(Harvester):
    """
    Class to harvest data from the OpenAlex API using the pyalex package.
    The default search field when not set is 'id' -- this corresponds to an entity's OpenAlex ID.

    To use, see generics.Harvester: add search_values (preferably list of SearchValue objects) and call get_results().
    The details on what the SearchValue object should/can contain can be found in this class.

    The results are stored in the _results attribute, which is a dictionary with the following structure:
    {
        "works": {work_id: {work_data}},
        "authors": {author_id: {author_data}},
        "sources": {source_id: {source_data}},
        "publishers": {publisher_id: {publisher_data}},
        "institutions": {institution_id: {institution_data}},
        "funders": {funder_id: {funder_data}},
        "topics": {topic_id: {topic_data}},
        "subfields": {subfield_id: {subfield_data}},
        "fields": {field_id: {field_data}},
        "domains": {domain_id: {domain_data}},
    }

    the keys are the OpenAlex IDs of the entities, and the values are the retrieved data as dicts.
    """

    # maps entity strings to the corresponding pyalex classes used for searching
    ENTITY_MAPPING: dict[SearchEntityType, BaseOpenAlex] = {
        SearchEntityType.WORK: Works,
        SearchEntityType.AUTHOR: Authors,
        SearchEntityType.SOURCE: Sources,
        SearchEntityType.PUBLISHER: Publishers,
        SearchEntityType.INSTITUTION: Institutions,
        SearchEntityType.FUNDER: Funders,
        SearchEntityType.TOPIC: Topics,
        SearchEntityType.SUBFIELD: Subfields,
        SearchEntityType.FIELD: Fields,
        SearchEntityType.DOMAIN: Domains,
    }

    # field names recognized by this class for searching
    VALID_FIELDNAMES: list[QueryValueType] = [
        QueryValueType.OPENALEX_ID,
        QueryValueType.DOI,
        QueryValueType.ROR,
        QueryValueType.ORCID,
        QueryValueType.ID,
        QueryValueType.NAME,
        QueryValueType.ISSN,
        QueryValueType.PMID,
        ]

    def __init__(self, settings):
        super().__init__(settings)
        self.default_search_field = "id"
        self.default_entity = "work"
        self._setup_pyalex()
        self._results: dict[str, dict[str, dict]] = {
            "works": {},
            "authors": {},
            "sources": {},
            "publishers": {},
            "institutions": {},
            "funders": {},
            "topics": {},
            "subfields": {},
            "fields": {},
            "domains": {},
        }

    def _setup_pyalex(self):
        pyalex.config.email = SETTINGS.user_email
        pyalex.config.max_retries = SETTINGS.openalex_settings.get("max_retries", 3)
        pyalex.config.retry_backoff_factor = SETTINGS.openalex_settings.get("retry_backoff_factor", 0.1)
        pyalex.config.retry_http_codes = SETTINGS.openalex_settings.get("retry_http_codes", [429, 500, 503])
        self.max_amount_of_pages = 10
        self.results_per_page = 200
        self.max_results_per_query = self.max_amount_of_pages * self.results_per_page
    def _validate_search_values(self) -> bool:
        """
        Check if self_search_values is not empty. Then:
        check if each entry in self._search_values has a value, field, and an entity that's found in ENTITY_MAPPING.
        If so, return True, otherwise False.
        """
        if not self._search_values:
            print("No search values set")
            return False
        for search_value in self._search_values:
            if search_value.entity not in self.ENTITY_MAPPING:
                print(f'Invalid entity: {search_value.entity}')
                return False
            if any([not search_value.field, not search_value.value]):
                print(f"either SearchValue.field or SearchValue.value is empty: {search_value}")
                return False
        return True




    def _construct_query(self, idlist:str, field:QueryValueType, entity_type:SearchEntityType) -> BaseOpenAlex:
        """
        This function constructs a query based on the given idlist, field, and entity_type.
        This is required to handle nested filter fields & to set the correct filters for a QueryValueType.
        For non-nested query fields that match QueryValueType values, we can construct it directly.
        """
        print(f'_construct_query called with:\n idlist: {idlist}\n field: {field}\n entity_type: {entity_type}')

        match field:
            case QueryValueType.ID | QueryValueType.OPENALEX_ID:
                return self.ENTITY_MAPPING[entity_type]().filter(openalex_id=idlist)
            case QueryValueType.DOI:
                return self.ENTITY_MAPPING[entity_type]().filter(doi=idlist)
            case QueryValueType.PMID:
                return self.ENTITY_MAPPING[entity_type]().filter(pmid=idlist)
            case QueryValueType.ROR:
                match entity_type:
                    case SearchEntityType.WORK:
                        return self.ENTITY_MAPPING[entity_type]().filter(institutions={'ror':idlist})
                    case SearchEntityType.AUTHOR:
                        return self.ENTITY_MAPPING[entity_type]().filter(affiliations={'institution':{'ror':idlist}})
                    case SearchEntityType.PUBLISHER | SearchEntityType.INSTITUTION | SearchEntityType.FUNDER:
                        return self.ENTITY_MAPPING[entity_type]().filter(ror=idlist)
            case QueryValueType.ORCID:
                return self.ENTITY_MAPPING[entity_type]().filter(orcid=idlist)
            case QueryValueType.NAME:
                return self.ENTITY_MAPPING[entity_type]().search(idlist)
            case QueryValueType.ISSN:
                match entity_type:
                    case SearchEntityType.WORK:
                        return self.ENTITY_MAPPING[entity_type]().filter(locations={"source":{"issn":idlist}})
                    case SearchEntityType.SOURCE:
                        return self.ENTITY_MAPPING[entity_type]().filter(issn=idlist)
            case _:
                print(f'Did not recognize field: {field} and/or entity_type: {entity_type}. Trying to return default query.')
                # use the value for 'field' as the keyword for filter() arg, set to value idlist
                # e.g. if field='openalex_id', then filter(openalex_id=idlist)
                try:
                    query = self.ENTITY_MAPPING[entity_type]().filter(**{field.value:idlist})
                    return query
                except Exception as e:
                    print(f"Error constructing query: {e}")
                    return None

    def _search(self):
        """
        This function parses the search values, constructs the queries, and the retrieves the results.
        It groups the queries by entity and field to be able to batch them into sets of 50 where possible.
        """

        if not self._validate_search_values():
            raise ValueError("Search values are not valid")

        searches:dict[SearchEntityType, dict[QueryValueType, list]] = defaultdict(lambda: defaultdict(set))
        for search_value in self._search_values:
            searches[search_value.entity][search_value.field].add(search_value.value)
        queries = defaultdict(list)
        num_items = 0
        for entity_type, fields in searches.items():
            if not fields:
                continue
            for field, values in fields.items():
                values = list(values)
                if field not in self.VALID_FIELDNAMES:
                    print(f"Invalid field name: {field}")
                    print(f'{entity_type} query will not be run for field {field} with value(s): {values}')
                    print(f'Note: valid field names are {self.VALID_FIELDNAMES}')
                    continue
                if len(values) > 1:
                    if field in [QueryValueType.ID, QueryValueType.OPENALEX_ID, QueryValueType.DOI, QueryValueType.ORCID, QueryValueType.ROR]:
                        if len(values) > 50:
                            for batch in batched(values, 50):
                                num_items += len(batch)
                                idlist = "|".join(batch)
                                constructed_query = self._construct_query(idlist, field, entity_type)
                                queries[entity_type.value+'s'].append(constructed_query)
                        else:
                            num_items += len(values)
                            idlist = "|".join(values)
                            constructed_query = self._construct_query(idlist, field, entity_type)
                            queries[entity_type.value+'s'].append(constructed_query)
                    else:
                        for value in values:
                            num_items += 1
                            queries[entity_type.value+'s'].append(self._construct_query(value, field, entity_type))
                else:
                    num_items += 1
                    queries[entity_type.value+'s'].append(self._construct_query(values[0], field, entity_type))

        if not queries:
            print("No queries to run.")
            return

        print(f'Running {len(queries)} {"queries" if len(queries) > 1 else 'query'} for {num_items} requested items.')
        self._retrieve_queries(queries)

    def _retrieve_queries(self, queries: dict[str,list[BaseOpenAlex]]) -> None:
        for entity_type, querylist in queries.items():
            print(f'Retrieving {len(querylist)} {entity_type} queries.')
            for num, query in enumerate(querylist, start=1):
                print(f'Running query {num}/{len(querylist)} for {entity_type}.')
                if isinstance(query, dict):
                    self._results[entity_type][query['id']] = query
                    continue

                print(f'Retrieving multiple {entity_type}. Limited to {self.max_results_per_query}.')
                for record in chain(*query.paginate(per_page=self.results_per_page, n_max=self.max_results_per_query)):
                    self._results[entity_type][record['id']] = record
