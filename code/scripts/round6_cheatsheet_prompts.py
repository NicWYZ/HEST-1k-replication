"""Round 6 cheatsheet track: the prompts of instruction 6.3, verbatim.

`{B}` is the size in bytes, digits only. The target is log1p of the raw count
(code/scripts/round6_cheatsheet_package.py), so "as log(1 + count)" stands and
the one permitted change of 6.3 is not used.

From C2 on, the last paragraph of each prompt carries the sentence the C1
memo (section 3.3) adds before "When the file is written, stop." The C1
pilot ran without it.
"""

WRITER = """You are working in a directory that holds measurements from one tissue section of human skin melanoma, profiled by spatial transcriptomics (10x Xenium, aggregated to spots). `patches/` holds one H&E image per spot, 224 by 224 pixels at 0.5 micrometres per pixel, named by spot ID. `spots.csv` gives each spot's position in pixels. `expression.csv` gives each spot's expression of 50 genes, as log(1 + count). `overview.png` is a low-resolution image of the whole section.

Later, a different agent will predict the expression of the same 50 genes from H&E patches of this kind of tissue. That agent will see only the patch images, under new IDs and without positions, and one text file written by you. It will not see these measurements.

Write that file as `cheatsheet.txt` in this directory. It may contain anything that you think will help the other agent predict accurately. It must be at most {B} bytes in UTF-8. Anything beyond {B} bytes will be cut off. You may use the tools available to you, including Python, to study the data. There is no internet access, and no pretrained models or files other than those in this directory are available. When the file is written, stop."""

PREDICTOR_P1 = """You are working in a directory that holds H&E images from a tissue section of human skin melanoma that was profiled by spatial transcriptomics (10x Xenium, aggregated to spots). `patches/` holds one H&E image per spot, 224 by 224 pixels at 0.5 micrometres per pixel, named by spot ID. `genes.txt` lists 50 genes."""

PREDICTOR_P2 = """`cheatsheet.txt` was written by someone who had measured the expression of these genes in tissue of this kind. Use it as a reference to help you make your predictions."""

PREDICTOR_P3 = """Predict the expression of each of the 50 genes at every spot, as log(1 + count). Write `predictions.csv` with one row per spot, a column `spot_id` followed by one column per gene, named as in `genes.txt`. Every spot and every gene must have a number. You may use the tools available to you, including Python. There is no internet access, and no pretrained models or files other than those in this directory are available. When the file is written, stop."""

PREDICTOR = PREDICTOR_P1 + "\n\n" + PREDICTOR_P2 + "\n\n" + PREDICTOR_P3
BASELINE = PREDICTOR_P1 + "\n\n" + PREDICTOR_P3

COMBINED = """You are working in a directory with two folders from spatial transcriptomics of human skin melanoma (10x Xenium, aggregated to spots). In `labelled/`, `patches/` holds one H&E image per spot, 224 by 224 pixels at 0.5 micrometres per pixel, named by spot ID, `spots.csv` gives each spot's position in pixels, `expression.csv` gives each spot's expression of 50 genes, as log(1 + count), and `overview.png` is a low-resolution image of the whole section those spots come from. In `target/`, `patches/` holds H&E images of the spots whose expression you are to predict, with no measurements, and `genes.txt` lists the 50 genes.

Predict the expression of each of the 50 genes at every spot in `target/patches/`, as log(1 + count). Write `predictions.csv` in this directory with one row per target spot, a column `spot_id` followed by one column per gene, named as in `target/genes.txt`. Every spot and every gene must have a number. You may use the tools available to you, including Python. There is no internet access, and no pretrained models or files other than those in this directory are available. When the file is written, stop."""


def prompt_for(role, size=None):
    if role == "writer":
        return WRITER.replace("{B}", str(int(size)))
    if role == "predictor":
        return PREDICTOR
    if role == "baseline":
        return BASELINE
    if role == "combined":
        return COMBINED
    raise ValueError(role)
