import marimo

__generated_with = "0.10.19"
app = marimo.App(width="medium")


@app.cell
def imports():
    import marimo as mo
    import constants
    from settings import SETTINGS
    from harvester_manager import HarvesterManager
    from harvesters.generics import SearchValue, SearchEntityType, QueryValueType
    return (
        HarvesterManager,
        QueryValueType,
        SETTINGS,
        SearchEntityType,
        SearchValue,
        constants,
        mo,
    )


@app.cell
def _(HarvesterManager, QueryValueType, SearchEntityType, SearchValue):
    manager = HarvesterManager()
    manager.add_search_values([
        SearchValue('https://doi.org/10.3168/jds.2020-19242', 'doi', 'work'),
        SearchValue('https://doi.org/10.1021/acs.analchem.9b05183', QueryValueType.DOI, SearchEntityType.WORK),
        SearchValue('https://openalex.org/S138962950', QueryValueType.OPENALEX_ID, SearchEntityType.SOURCE),
        SearchValue('https://openalex.org/I94624287', QueryValueType.OPENALEX_ID, SearchEntityType.INSTITUTION),
        SearchValue("https://orcid.org/0000-0002-4769-5239", QueryValueType.ORCID, SearchEntityType.AUTHOR),
        SearchValue("https://ror.org/006hf6230", QueryValueType.ROR, SearchEntityType.WORK),
    ])
    print(manager.harvesters['openalex'].search_values)
    print(len(manager.harvesters['openalex'].search_values))
    return (manager,)


@app.cell(disabled=True)
def _(manager):
    results = manager.harvesters['openalex'].get_results(True)
    print(results.keys())
    return (results,)


@app.cell
def _(results):
    for itemtype, items in results.items():
        print(f"got {len(items)} {itemtype}")
    return items, itemtype


if __name__ == "__main__":
    app.run()
