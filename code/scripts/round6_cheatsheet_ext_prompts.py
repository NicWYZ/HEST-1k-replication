"""Round 6 extension, cheatsheet track: the prompts and RULES.md, verbatim.

Generated from instruction section 6.3 and 6.4
(docs/round06/i04/cheatsheet/round06_cheatsheet_ext_track.md) by copying each
quoted block with its quote markers removed. `python
round6_cheatsheet_ext_prompts.py --check INSTRUCTION.md` extracts the blocks
again and fails if any differs from the text held here.

{B} is the size in bytes, digits only. {VIOLATIONS} is the checker's list.
TARGET_PHRASE is the one phrase instruction 6.3 allows to change, if C4 finds
the target is not the natural log of one plus the count.
"""
import sys

TARGET_PHRASE = "as log(1 + count)"

WRITER = "You are working in a directory that holds measurements from tissue sections of human clear cell renal cell carcinoma from seven patients, profiled by spatial transcriptomics (10x Visium, spots 55 micrometres across). `patches/` holds one H&E image per spot, 224 by 224 pixels at 0.5 micrometres per pixel, centred on the spot and named by spot ID. `spots.csv` gives each spot's patient, as a label from P1 to P7, and its position in pixels on that patient's section. `expression.csv` gives each spot's expression of 50 genes, as log(1 + count). The spots of each patient are a sample of 500 from that section. `overviews/` holds a low-resolution image of each patient's section.\n\nLater, a different agent will predict the expression of the same 50 genes from H&E patches of this kind of tissue taken from other patients. That agent will see only the patch images and one text file written by you. It will not see these measurements or these patients.\n\nWrite that file as `cheatsheet.txt` in this directory. It should pass on, in words and numbers, what this tissue looks like and how its appearance relates to the expression of these genes, in a form that will hold for new patients. It must follow the rules in `RULES.md`, and it must be at most {B} bytes in UTF-8. Anything beyond {B} bytes will be cut off. Use as much of the allowed size as helps; more detail is generally better. Look at patches from every patient. Before you finish, run `python3 check_cheatsheet.py`, which reports the size and possible problems, and fix those that break the rules. You may use the tools available to you, including Python, to study the data. There is no internet access, and no pretrained models or files other than those in this directory are available. When the file is written and the check passes, stop."

REVISION = 'An independent reviewer checked `cheatsheet.txt` against `RULES.md` and found the problems listed below. Revise `cheatsheet.txt` so that it follows every rule and stays within {B} bytes. Run `python3 check_cheatsheet.py` again before you finish, and fix what it reports that breaks the rules. When the revised file is written and the check passes, stop.\n\n{VIOLATIONS}'

CHECKER = 'You are reviewing a text file, `cheatsheet.txt`, against the rules in `RULES.md`. `genes.txt` lists the 50 genes the file is about. Read both files in full. For every passage that breaks a rule, give its line numbers, the number of the rule it breaks, and one sentence saying why. Judge only whether the file follows the rules, not whether its content is correct or useful. Write `verdict.json` in this directory as a JSON object with a key `pass`, true or false, and a key `violations`, a list of objects with keys `lines`, `rule` and `reason`. The file passes only if the list is empty. When `verdict.json` is written, stop.'

PREDICTOR = 'You are working in a directory that holds H&E images from tissue sections of human clear cell renal cell carcinoma from three patients, profiled by spatial transcriptomics (10x Visium, spots 55 micrometres across). `patches/a/`, `patches/b/` and `patches/c/` each hold the patches of one patient, one H&E image per spot, 224 by 224 pixels at 0.5 micrometres per pixel, centred on the spot and named by spot ID. `genes.txt` lists 50 genes.\n\n`cheatsheet.txt` was written by someone who had measured the expression of these genes in this kind of tissue from other patients. Use it as a reference to help you make your predictions.\n\nPredict the expression of each of the 50 genes at every spot, as log(1 + count). Write `predictions.csv` with one row per spot, a column `spot_id` followed by one column per gene, named as in `genes.txt`. Every spot and every gene must have a number. You may use the tools available to you, including Python. There is no internet access, and no pretrained models or files other than those in this directory are available. When the file is written, stop.'

COMBINED = "You are working in a directory with two folders from spatial transcriptomics of human clear cell renal cell carcinoma (10x Visium, spots 55 micrometres across). In `labelled/`, from seven patients, `patches/` holds one H&E image per spot, 224 by 224 pixels at 0.5 micrometres per pixel, centred on the spot and named by spot ID, `spots.csv` gives each spot's patient, as a label from P1 to P7, and its position in pixels on that patient's section, `expression.csv` gives each spot's expression of 50 genes, as log(1 + count), and `overviews/` holds a low-resolution image of each patient's section. In `target/`, from three other patients, `patches/a/`, `patches/b/` and `patches/c/` hold the H&E images of the spots whose expression you are to predict, one folder per patient, and `genes.txt` lists the 50 genes.\n\nPredict the expression of each of the 50 genes at every spot in `target/patches/`, as log(1 + count). Write `predictions.csv` in this directory with one row per target spot, a column `spot_id` followed by one column per gene, named as in `target/genes.txt`. Every spot and every gene must have a number. You may use the tools available to you, including Python. There is no internet access, and no pretrained models or files other than those in this directory are available. When the file is written, stop."

RULES_MD = '# Rules for `cheatsheet.txt`\n\nThe file is for an agent that will look at H&E patches from patients you have not seen and predict the expression of the 50 genes. Everything in it must be something a pathologist could apply while looking at one patch from a new patient, without a computer. That is the test for every sentence.\n\n## Allowed\n\n- **A1.** Tissue and cell types, structures and states, described in histological terms. For example, clear-cell tumour nests with a fine capillary network, eosinophilic or granular tumour cells, lymphoid aggregates, fibrous stroma, necrosis, haemorrhage, normal tubules or glomeruli.\n- **A2.** The expression of any of the 50 genes in each described class, in numbers (means, typical ranges, quantiles) or in words.\n- **A3.** How expression changes with something visible, such as the density of lymphocytes, the share of the patch that is stroma, or the presence of vessels, described so that it can be judged by eye.\n- **A4.** Groups of genes that rise and fall together, and the biology behind them.\n- **A5.** How patients differ, described by what their tissue looks like and without saying which patient. "In some patients the tumour cells are granular and eosinophilic, and there CA9 is lower" is allowed. "Patient P3 had granular cells" is not (F3).\n- **A6.** Cautions about appearance, such as staining that varies between sections, and what to look at instead.\n- **A7.** The overall level and spread of each gene across tissue of this kind.\n\nEstimates by eye are allowed, such as "about half of the patch is empty space". So are rules a person applies by eye, such as "decide which of these classes the patch looks most like, then use that class\'s values" or "if the patch is mostly stroma, expect COL1A1 to be high".\n\n## Forbidden\n\n- **F1.** Code, pseudocode, formulas over pixel values, and instructions for fitting, training or running any model or algorithm on computed data (for example regression, nearest neighbours, clustering, or thresholds on computed features). Rules applied by eye, as above, are not covered by this rule.\n- **F2.** Image measurements that need a computer, such as mean colour values, pixel counts or fractions computed from pixels, texture or frequency statistics, or colour-space conversions.\n- **F3.** Anything keyed to an individual training spot, section or patient, including spot IDs, patient labels, positions, image fingerprints, or tables with one row per spot.\n- **F4.** Encoded, compressed or otherwise unreadable data.\n- **F5.** Advice about the scoring metric, or about transforming or rescaling predictions in order to score well. Typical levels and spreads of genes are A7 and are allowed.\n- **F6.** Technical properties used as predictors, such as file properties, image size, scanner, batch or section quality, unless described as visible tissue appearance.\n'



def baseline_prompt():
    """The predictor's prompt without its second paragraph."""
    paras = PREDICTOR.split("\n\n")
    assert len(paras) == 3
    return paras[0] + "\n\n" + paras[2]


def render(role, b=None, violations=None):
    if role == "writer":
        return WRITER.replace("{B}", str(int(b)))
    if role == "revision":
        return REVISION.replace("{B}", str(int(b))).replace("{VIOLATIONS}", violations)
    return {"checker": CHECKER, "predictor": PREDICTOR, "baseline": baseline_prompt(), "combined": COMBINED}[role]


def _extract(path):
    L = open(path).read().split("\n")

    def block(start, after=0):
        i = next(k for k, l in enumerate(L) if k >= after and l.startswith(start))
        j = next(k for k in range(i, len(L)) if L[k].startswith(">"))
        out = []
        while j < len(L) and L[j].startswith(">"):
            out.append(L[j][2:] if L[j].startswith("> ") else L[j][1:])
            j += 1
        return "\n".join(out)

    i = next(k for k, l in enumerate(L) if l.startswith("### 6.4"))
    return {"WRITER": block("**Writer.**"), "REVISION": block("**Writer revision**"),
            "CHECKER": block("**Checker.**"), "PREDICTOR": block("**Predictor.**"),
            "COMBINED": block("**Combined session.**"), "RULES_MD": block("---", i) + "\n"}


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--check":
        got = _extract(sys.argv[2])
        bad = [k for k, v in got.items() if v != globals()[k]]
        print("prompts and rules match the instruction" if not bad else f"DIFFER: {bad}")
        sys.exit(1 if bad else 0)
