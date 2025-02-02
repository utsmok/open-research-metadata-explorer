"""
This module is centered on the HarvesterManager class, which can be used to create and manage harvesters for various sources.
"""

from settings import SETTINGS, Source
from harvesters.generics import Harvester, SearchValue, SearchEntityType, QueryValueType
from harvesters.openalex import OpenAlexHarvester
from harvesters.not_yet_implemented import *

class HarvesterManager:
    """
    Use to run harvesters & retrieve their data.
    On init: Creates harvesters based on contents of settings.sources
    """
    HARVESTER_MAPPING = {
            "crossref": CrossrefHarvester,
            "openalex": OpenAlexHarvester,
            "semantic_scholar": SemanticScholarHarvester,
            "zenodo": ZenodoHarvester,
            "datacite": DataCiteHarvester,
            "openaire": OpenAIREHarvester,
            "openapc": OpenAPCHarvester,
            "core": COREHarvester,
            "base": BASEHarvester,
            "pubmed": PubmedHarvester,
            "arxiv": ArxivHarvester,
            "unpaywall": UnpaywallHarvester,
            "journal_browser": JournalBrowserHarvester,
            "doaj": DOAJHarvester,
        }

    harvesters: dict[str, Harvester] = {}
    disabled_harvesters: dict[str, Harvester] = {}
    def __init__(self):
        for source in SETTINGS.sources:
            if source.enabled:
                self.harvesters[source.name] = self._create_harvester(source)

    def enable_harvester(self, source_name: str) -> None:
        """Enable/add a harvester"""
        if source_name in self.disabled_harvesters:
            self.harvesters[source_name] = self.disabled_harvesters[source_name]
            del self.disabled_harvesters[source_name]
        else:
            self.harvesters[source_name] = self._create_harvester(Source(source_name, True))

    def disable_harvester(self, source_name: str) -> None:
        """Disable a harvester"""
        if source_name in self.harvesters:
            self.disabled_harvesters[source_name] = self.harvesters[source_name]
            del self.harvesters[source_name]
        else:
            print(f"Harvester {source_name} not found in enabled harvesters. Current harvesters: {self.harvesters.keys()}")

    def _create_harvester(self, source: Source) -> Harvester:
        """Create a harvester for the given source"""
        harvest_class = self.HARVESTER_MAPPING.get(source.name.lower())
        if harvest_class:
            return harvest_class(source)
        else:
            raise ValueError(f"Cannot determine harvester for: {source}")

    def add_search_values(self, entity_type: SearchEntityType, value_type: QueryValueType, values: list[str]) -> None:
        """
        Add search values to all enabled harvesters that can handle the given entity type.
        The manager will make sure they are added correctly (i.e. as SearchValue objects with correct field values etc).
        """
        # TODO: implement this -- map entity and value types to match the harvester's search fields etc
        for harvester_name, harvester in self.harvesters.items():
            if entity_type in harvester.ENTITY_MAPPING:
                search_values = [SearchValue(value, value_type, entity_type) for value in values]
                harvester.search_values = search_values
