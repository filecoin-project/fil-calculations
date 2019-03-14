# fil-calculations

## Config

Notebooks should be edited using `.md` for version-control-friendly source.
- To use `.md` (required), append to `jupyter_notebook_config.py`:
```
c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
c.ContentsManager.default_jupytext_formats = "ipynb,md"
```
