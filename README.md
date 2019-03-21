# Filecoin Parameter Calculations

## NOTE

All code and notebooks contained here are very rough. The eventual goal is to unify existing calculators into a 
version-controlled and well-documented library. However, the primary immediate use is to analyze and project 
performance, synthesizing theoretical calculations with actual performance data. This is a dirty problem, and the 
work product reflects the nature of trying to draw a bead on a moving target. The first and foremost goal is to find 
a firing solution that will allow us to meet both security and scaling requirements for Proof of Replication. This is
 like searching for a needle in a haystack, but the end is in sight.
 
Until that happens, this work should be seens as an artifact of that effort. Over time, the goal is to tame the complexity 
(then well-understood and stabilized) and refactor the resulting model for clarity and auditable explanatory power.

## Environment

Create the conda environment:

```console
> conda env create -f environment.yml
```

Activate it:
```console
> conda activate fil-calculations
```

## Notebook Config

Notebooks should be saved in both `.md` and `.ipynb`.
- To use `.md` (required), append to `jupyter_notebook_config.py`:
```
c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
c.ContentsManager.default_jupytext_formats = "ipynb,md"
```

## Local Notebooks

From project root:
```console
> cd fil-calculations
> jupyter notebook
````

## Version Control

Always load and save any notebooks which may have changed so that the `.ipynb` files have accurate values. In 
particular, this makes the non-interactive view available on GitHub useful.

TODO: Script this. Eventually verify on CI.

## Entry Points

 - [Proof Scalling](fil-calculations/proof_scaling.ipynb)
 - [ZigZag Performance](fil-calculations/zigzag_performance.ipynb)
 - [Apex Optimization](fil-calculations/apex.ipynb)


# License

The Filecoin Project is dual-licensed under Apache 2.0 and MIT terms:

- Apache License, Version 2.0, ([LICENSE-APACHE](../LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](../LICENSE-MIT) or http://opensource.org/licenses/MIT)
