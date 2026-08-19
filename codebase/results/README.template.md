# Sweep-group README template

This template applies to a result group whose files come from sweeping one script over a job
list and spreading across chart-kind and, usually, axis-basis subfolders. Such a group nests
more than one level below `results/<group>/`. A flat group, a handful of files with no
repeated subfolder shape, does not need its own README. Its description belongs inline in
`results/README.md` instead.

The author copies the sections below into `results/<group>/README.md` and fills each one
from the generating script, not from memory. Three stale docs that this template replaces,
`directory_tree.txt`, the old `Thesis/README.md` Results table, and `snapshot_study.py`'s own
docstring, drifted because someone wrote the shape down once while the code kept moving.

---

## Purpose

One or two sentences: which physical quantity this group plots, and why it exists (what
question it answers).

## Generating script

Path to the script, and one line: what input it reads (which pipeline stage's output) and what
config module supplies its job list and output root.

## Sweep dimensions

| Dimension | Source of truth | Values |
|---|---|---|
| *(for example, pool × fee-tier)* | *(for example, `data_extraction/config.py POOLS`)* | *(count and range)* |
| *(for example, axis-basis)* | *(hardcoded in the script, for example `_AXES`)* | *(list)* |

## Directory shape

```
<group>/
├── <chart-kind>/
│   ├── <axis-basis>/
│   │   └── <fee>bp_<PAIR>.png
│   └── ...
└── <flat chart-kind, if any>/
    └── <fee>bp_<PAIR>.png
```

The page states which chart-kinds spread across axis-basis and which stay flat, one file per
job. Each group's own scripts decide that per chart-kind; no fixed rule spans all groups.

## File-naming pattern

`<pattern>`. The page decodes each token: its possible values, and where the value is defined.

## How to read one file

The page picks one real path from the tree and decodes it token by token, then adds one
sentence on what the plot itself shows: its axes, and what a reader should notice.
