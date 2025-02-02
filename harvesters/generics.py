from dataclasses import dataclass, field
from settings import Source
from enum import Enum
class QueryValueType(Enum):
    """
    Contains all recognized query value types (aka 'field' or 'search field' etc) for searching.
    Each Harvester class will define a list of valid field names to use for searching, and handle the mapping between these and the actual search fields.
    """
    OPENALEX_ID = "openalex_id"
    OPENAIRE_ID = "openaire_id"
    DOI = "doi"
    ROR = "ror"
    ORCID = "orcid"
    ISBN = "isbn"
    ISSN = "issn"
    PMID = "pmid"
    ID = "id"
    NAME = "name"
    # these values below are meant to be used as additional filters
    PUBLICATION_YEAR = "publication_year"
    PUBLICATION_DATE = "publication_date"
    PUBLISHER = "publisher"
    OA_STATUS = "oa_status"
    IS_OA = "is_oa"
    TYPE = "type"




class SearchEntityType(Enum):
    """
    Contains all recognized entity types for searching.
    Each Harvester class will define a list of valid entity types supported by that API,
    and handle the mapping between these values and the entities / endpoints in the API.
    """
    WORK = "work"
    DATASET = "dataset"
    SOFTWARE = "software"
    AUTHOR = "author"
    SOURCE = "source"
    PUBLISHER = "publisher"
    INSTITUTION = "institution"
    FUNDER = "funder"
    TOPIC = "topic"
    SUBFIELD = "subfield"
    FIELD = "field"
    DOMAIN = "domain"
    PROJECT = "project"
    GRANT = "grant"
    LICENSE = "license"
    JOURNAL = "journal"

@dataclass
class SearchValue:
    """
    Stores a search value, the type to search for, and which search field to use.
    The 'field' and 'entity' fields should be of type QueryValueType and SearchEntityType respectively.
    If initialized with strings, they are converted to the corresponding Enum entries during init.

    Optionally, additional filters can be added to the search value. This is a list of SearchValue objects that can be used to filter the search results further -- e.g. to filter by year or other metadata.
    Do not change field or entity values after initialization (for now)
    """
    value: str
    field: QueryValueType | str
    entity: SearchEntityType | str
    additional_filters: list["SearchValue"] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.field, str):
            self.field = QueryValueType[self.field.upper()]
        if isinstance(self.entity, str):
            self.entity = SearchEntityType[self.entity.upper()]

class Harvester:
    """Base class for harvesters"""

    settings: Source
    _search_values: list[SearchValue] = list()
    _results: dict[str,dict] = dict() # store the harvest results here. key: inputted search value, value: retrieved result
    default_search_field: str = "id"
    default_entity: str = "work"

    # stores the mapping between entity types and the corresponding functions or classes used for searching by the implementing class
    ENTITY_MAPPING: dict[SearchEntityType, any] = dict()
    # stores the valid field names recognized by the implementing class for searching
    VALID_FIELDNAMES: list[QueryValueType]
    def __init__(self, settings: Source):
        self.settings = settings

    @property
    def search_values(self) -> list[SearchValue]:
        return self._search_values

    @search_values.setter
    def search_values(self, values: list[SearchValue]|list[dict]|list[tuple]|list[str]) -> None:
        """
        Set the values to search for.
        Can be a list of strings, dicts, tuples or SearchValue objects.
        Should contain a value, field, and entity type for each search term (all strs).
        For a list of strings, self.default_search_field is used for 'field' (default = "id").
        Otherwise, it takes the 'field' from the dict, tuple or SearchValue object.
        Same goes for the 'entity' field, which defaults to "work".
        """
        if not isinstance(values, list):
            raise ValueError("search_values must be a list")
        if all(isinstance(value, str) for value in values):
            values = [SearchValue(value, self.default_search_field, self.default_entity) for value in values]
        elif all(isinstance(value, dict) for value in values):
            values = [SearchValue(**value) for value in values]
        elif all(isinstance(value, tuple) for value in values):
            values = [SearchValue(*value) for value in values]
        elif all(isinstance(value, SearchValue) for value in values):
            values = values
        else:
            raise ValueError("search_values must be a list of strings, dicts, tuples or SearchValue objects")

        values = [value for value in values if value not in self._search_values]
        self._search_values.extend(values)


    def _search(self) -> None:
        """Search for the given search values and store the results"""
        raise NotImplementedError("Implement the search method")

    def get_results(self, refresh: bool = False) -> dict[str,dict]:
        """
        Return the results of the search.
        If no results are present, run the search first.
        If refresh is True, run the search again regardless of results.
        """
        if not self._results or refresh:
            if not self._search_values:
                raise ValueError("No search values set, cannot retrieve results")
            self._search()
        return self._results
