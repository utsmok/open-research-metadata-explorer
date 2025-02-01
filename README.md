# Open Research Metadata Explorer
A tool that lets you retrieve & view open research metadata for publications, built using Python & marimo, with data from OpenAlex, Crossref, Semantic Scholar, Zenodo, OpenAIRE, DataCite, and more.

## App demo
You can run the app directly by making use of [marimo.app](https://marimo.app/github.com/utsmok/open-research-metadata-explorer/blob/main/interface.py). Note that all the code will be running locally, and nothing is sent to the servers: your data will be private.

## Running locally
First make sure uv is installed. See below for instructions on how to do so.


<details>

<summary>Installing uv</summary>

We recommend [uv](https://docs.astral.sh/uv/) to install, manage & run python. If you haven't installed uv yet, you can do so with a single line of code:

**Windows**: open `PowerShell` and run this command:
```pwsh
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
**MacOS/Linux**: open a bash-compliant terminal and run:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
you can also use `wget` instead of `curl` if necessary:
```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```
</details>

# Local development

For local development we suggest to clone the repo first, see below for instructions.

<details>

<summary>Clone this repo to a folder on your machine</summary>
- using the githib cli: `gh repo clone utsmok/open-research-metadata-explorer`
- using git: `git clone https://github.com/utsmok/open-research-metadata-explorer`

- manually: navigate to the [repo on github.com](https://github.com/utsmok/open-research-metadata-explorer), click on the green `<> Code` button, and press `Download ZIP`. Extract to a new folder on your machine.

</details>

Then, you can run or edit the app like so:

0. Open the terminal of your choice (the one you installed `uv` for)
1. Navigate to the dir with the repo, e.g. `cd c:\dev\open-research-metadata-explorer\`
2. Initialize the environment with the command `uv sync`. This will automatically do a local install of python with all dependencies required.
3. Run the app with the command: `uv run marimo run interface.py`. This should open the app in your browser.
4. For development, change `marimo run` to `marimo edit`.
