import marimo

__generated_with = "0.10.19"
app = marimo.App(width="medium")


@app.cell
def imports():
    import marimo as mo
    import constants
    from settings import SETTINGS
    from harvester_manager import HarvesterManager
    from harvesters.generics import SearchValue
    return HarvesterManager, SETTINGS, SearchValue, constants, mo


@app.cell
def _(HarvesterManager, SearchValue):
    manager = HarvesterManager()

    manager.add_search_values = [
        SearchValue('https://doi.org/10.3168/jds.2020-19242', 'doi', 'work'),
        SearchValue('https://doi.org/10.1021/acs.analchem.9b05183', 'doi', 'work'),
        SearchValue('https://openalex.org/S138962950', 'openalex_id', 'source'),
        SearchValue('https://openalex.org/I94624287', 'openalex_id', 'institution'),
        SearchValue("https://orcid.org/0000-0002-4769-5239", "orcid", "author"),
    ]
    print(manager.harvesters['openalex'].search_values)
    return (manager,)


@app.cell
def _(manager):
    results = manager.harvesters['openalex'].get_results(True)
    print(results.keys())
    return (results,)


if __name__ == "__main__":
    app.run()
