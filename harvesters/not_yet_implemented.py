from harvesters.generics import Harvester

class CrossrefHarvester(Harvester):
    """Class to harvest data from the Crossref API using the habanero package"""
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
