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

    def add_single_type_search_values(self, entity_type: SearchEntityType, value_type: QueryValueType, values: list[str]) -> None:
        """
        For a given entity and value type, add search values to all enabled harvesters that can handle the given entity type.
        The manager will create the SearchValue instances based on the input.
        """
        # TODO: implement this -- map entity and value types to match the harvester's search fields etc
        for harvester_name, harvester in self.harvesters.items():
            print(f"Adding search values to {harvester_name}")

            if entity_type in harvester.ENTITY_MAPPING:
                search_values = [SearchValue(value, value_type, entity_type) for value in values]
                harvester.search_values = search_values
                print(f"Added {len(search_values)} search values to {harvester_name}")

    def add_search_values(self, search_values: list[SearchValue]) -> None:
        """
        Add search values to all enabled harvesters.
        """
        if not search_values:
            print("No search values provided")
            return
        for harvester_name, harvester in self.harvesters.items():
            valid_values = list()
            valid_entities = harvester.ENTITY_MAPPING.keys()
            for entry in search_values:
                for valid_type in valid_entities:
                    if entry.entity is valid_type:
                        valid_values.append(entry)
                        break
            if not valid_values:
                print(f"No compatible search values received for {harvester_name}")
                continue
            harvester.search_values = valid_values
            print(f"Added {len(valid_values)} search values to {harvester_name}")
