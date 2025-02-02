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
    ENTITY_MAPPING: dict[str, BaseOpenAlex] = {
        "work": Works,
        "author": Authors,
        "source": Sources,
        "publisher": Publishers,
        "institution": Institutions,
        "funder": Funders,
        "topic": Topics,
        "subfield": Subfields,
        "field": Fields,
        "domain": Domains,
    }

    # field names recognized by this class for searching
    VALID_FIELDNAMES: list[QueryValueType] = [QueryValueType('openalex_id'), QueryValueType('doi'), QueryValueType('ror'), QueryValueType('orcid'), QueryValueType('id')]

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
            if search_value.entity.value not in self.ENTITY_MAPPING:
                print(f'Invalid entity: {search_value.entity}')
                return False
            if any([not search_value.field, not search_value.value]):
                print(f"either SearchValue.field or SearchValue.value is empty: {search_value}")
                return False
        return True


    def _search(self):
        def construct_query(idlist:str, field:QueryValueType, entity_type:str):
            print(f'construct_query called with:\n idlist: {idlist}\n field: {field}\n entity_type: {entity_type}')
            if field == QueryValueType('id') or field == QueryValueType('openalex_id'):
                print(' selected filter field = openalex_id')
                return self.ENTITY_MAPPING[entity_type]().filter(openalex_id=idlist)
            elif field == QueryValueType('doi'):
                print(' selected filter field = doi')
                return self.ENTITY_MAPPING[entity_type]().filter(doi=idlist)
            elif field == QueryValueType('ror'):
                if entity_type == 'work':
                    print(' selected filter field => work: institutions.ror')
                    return self.ENTITY_MAPPING[entity_type]().filter(institutions={'ror':idlist})
                elif entity_type == 'author':
                    print(' selected filter field => author: affiliations.institution.ror')
                    return self.ENTITY_MAPPING[entity_type]().filter(affiliations={'institution':{'ror':idlist}})
                elif entity_type == 'institution' or entity_type == 'publisher' or entity_type == 'funder':
                    print(f' selected filter field => {entity_type}: ror')
                    return self.ENTITY_MAPPING[entity_type]().filter(ror=idlist)
            elif field == QueryValueType('orcid'):
                print(' selected filter field = orcid')
                return self.ENTITY_MAPPING[entity_type]().filter(orcid=idlist)


        if not self._validate_search_values():
            raise ValueError("Search values are not valid")

        searches:dict[str, dict[QueryValueType, list]] = defaultdict(lambda: defaultdict(list))
        for search_value in self._search_values:
            searches[search_value.entity.value][search_value.field].append(search_value.value)

        queries = defaultdict(list)
        num_items = 0
        for entity_type, fields in searches.items():
            print(f'entity_type: {entity_type}')
            print(f'fields.items(): {fields.items()}')
            if not fields:
                continue
            for field, values in fields.items():
                if field not in self.VALID_FIELDNAMES:
                    print(f"Invalid field name: {field}")
                    print(f'{entity_type} query will not be run for field {field} with value(s): {values}')
                    print(f'Note: valid field names are {self.VALID_FIELDNAMES}')
                    continue
                if len(values) > 1:
                    for batch in batched(values, 50):
                        num_items += len(batch)
                        idlist = "|".join(batch)
                        print('idlist:', idlist)
                        constructed_query = construct_query(idlist, field, entity_type)
                        print(f'constructed_query: {constructed_query}')
                        queries[entity_type+'s'].append(constructed_query)
                else:
                    num_items += 1
                    queries[entity_type+'s'].append(construct_query(values[0], field, entity_type))

        if not queries:
            print("No queries to run.")
            return

        print(f'Running {len(queries)} {"queries" if len(queries) > 1 else 'query'} for {num_items} requested items.')
        print(queries)
        self._retrieve_queries(queries)

    def _retrieve_queries(self, queries: dict[str,list[BaseOpenAlex]]) -> None:
        for entity_type, querylist in queries.items():
            print(f'Retrieving {len(querylist)} {entity_type} queries.')
            for num, query in enumerate(querylist, start=1):
                print(f'Running query {num}/{len(querylist)}')
                print(query)
                if isinstance(query, dict):
                    self._results[entity_type][query['id']] = query
                    continue
                for record in chain(*query.paginate(per_page=200)):
                    print(record.get('id'))
                    self._results[entity_type][record['id']] = record
