"""
This module contains functionality to retrieve data from the various APIs/sources.
These sources are:
- Crossref
- OpenAlex
- Semantic Scholar
- Zenodo
- DataCite
- OpenAIRE

- ... (more to be added)
"""

class Harvester:
    """Base class for harvesters"""
    ...

    def __init__(self, settings: dict = {}):
        self.settings = settings


class CrossrefHarvester(Harvester):
    """Class to harvest data from the Crossref API using the habanero package"""
    ...

class OpenAlexHarvester(Harvester):
    """Class to harvest data from the OpenAlex API using the pyalex package"""
    ...

class SemanticScholarHarvester(Harvester):
    """Class to harvest data from the Semantic Scholar API using the semanticscholar package"""
    ...

class ZenodoHarvester(Harvester):
    """Class to harvest data from the Zenodo API"""
    ...

class DataCiteHarvester(Harvester):
    """Class to harvest data from the DataCite API"""
    ...

class OpenAIREHarvester(Harvester):
    """Class to harvest data from the OpenAIRE API"""
    ...

class UnpaywallHarvester(Harvester):
    """Class to harvest data from the Unpaywall API"""
    ...

class JournalBrowserHarvester(Harvester):
    """Class to harvest data from the Journal Browser"""
    ...

class DOAJHarvester(Harvester):
    """Class to harvest data from the DOAJ API"""
    ...

class OpenAPCHarvester(Harvester):
    """
    Class to harvest data from the OpenAPC dataset
    https://github.com/OpenAPC/openapc-de

    This dataset contains APC data for ~240.000 articles from 450 institutions. This data can be used both for direct APC information,
    but also to determine a APC estimate for a given publisher/journal/year.

    The main data is stored as a CSV file. So, retrieve that file, and then extract the data from it.
    """
    ...

class COREHarvester(Harvester):
    """Class to harvest data from the CORE API"""
    ...

class BASEHarvester(Harvester):
    """Class to harvest data from the BASE API"""
    ...

class PubmedHarvester(Harvester):
    """Class to harvest data from the Pubmed API"""
    ...

class ArxivHarvester(Harvester):
    """Class to harvest data from the ArXiv API"""
    ...


class HarvesterFactory:
    """Factory class to create harvesters"""
    def __init__(self):
        self.harvesters = {
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

    def create_harvester(self, source: str, settings: dict = {}) -> Harvester:
        """Create a harvester for the given source"""
        return self.harvesters.get(source.lower(), Harvester)(settings)
