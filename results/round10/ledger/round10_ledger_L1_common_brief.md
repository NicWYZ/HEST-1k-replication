# Common brief for the L1 ledger subagents (7 November 2026)

You write the methods-ledger rows for one section of an applied statistics paper. Repository clone the oversight chat's clone, read only (edit nothing, no git commands that change anything). Read first: `docs/round10/i01/ledger/round10_ledger_L0_scope.md` (the scope), `docs/round10/i01/ledger/round10_ledger_brief.md` (standards), and `docs/round10/00_prep/round10_findings_survey.md` section 2 (the findings, with ids). The script inventory is in the claude.ai project doc, which you cannot read; use the headers of `code/scripts/` and `docs/environment.md` instead, and the round documents the findings cite.

For each result in your section, write one row with these fields:
1. Result (finding id and one sentence).
2. The existing method applied, named as the literature names it.
3. Source(s): author, year, venue, identifier (arXiv id or DOI). Open the source. Record the read level honestly: "full text" (say which sections), "abstract only", "not opened (reason)". You may use WebSearch and WebFetch; arXiv abstract pages and open PDFs are usually reachable, paywalled ones are not. Never cite a source you did not open; mark it "not opened" if the record cites it and you could not reach it.
4. Where the record already found this source (round and document path), if it did.
5. Implementation: the script in `code/scripts/` and the function, from the script's header or code.
6. What the record validated about it and where (document path, result file).
7. What is missing for the paper (unread source, unverified textbook citation, no variance estimator, no standard error, rerun needed, etc.).
8. Gap: only if no existing method was found after searching survey sampling, econometrics and machine learning venues; give the queries that failed.

Keep a query log as a CSV with columns date, query, engine, hits, kept, note. Search survey sampling as well as machine learning. Do not derive, do not propose new methods, do not decide the open questions; where a question is in your section (E, P, R7-6, V, D5), collect what the literature says and list the candidate sources, with read levels.

Prose rules: plain prose, no em-dashes, no colon-then-explanation sentences, math in LaTeX. Every number read back from the file you cite, with its path.

Outputs: `round10_ledger_L1_<section>.md` (written in the session's scratch folder, copied here) (the rows, as a table or as numbered entries) and `results/round10/ledger/L1_<section>_queries.csv`. Aim for completeness over length. Finish with a short list of sources the oversight chat should read in full at L2 and could not reach from here, each with a DOI or arXiv id.
