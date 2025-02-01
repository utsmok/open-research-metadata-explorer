import marimo

__generated_with = "0.10.19"
app = marimo.App(width="medium")


@app.cell
def imports():
    import marimo as mo
    import constants
    from settings import SETTINGS
    return SETTINGS, constants, mo


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
