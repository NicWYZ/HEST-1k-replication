#!/usr/bin/env python3
"""Standalone fetch of the 2018 ACS PUMS person file (1-Year horizon, 50 states and DC) through folktables.

Usage: python acs_pums2018_fetch.py OUTDIR

Needs only folktables, pandas, pyarrow (plus the standard library). Writes under OUTDIR:
  raw/2018/1-Year/psam_pNN.csv   the Census csv of every state, untouched, every column
  acs_pums2018_all_columns.parquet  every column of every row, explicit pyarrow schema
  raw_manifest.json              file name, source URL, bytes, md5, rows
  fetch_info.json                folktables/pandas/pyarrow versions, call made, state list, schema
  REFUSAL.txt                    only if the download or read fails; then the script exits 2

folktables 0.0.12 lists 50 states and PR but not DC, so its assertion would reject 'DC'.
This script adds DC (FIPS 11) to folktables' own two lookup tables in memory and then makes the
ordinary ACSDataSource(...).get_data(states=..., download=True) call. The URL pattern is the same.
folktables deletes each downloaded zip after extracting its csv, so md5s are of the csv files.
"""
import hashlib, io, json, os, sys, traceback, contextlib, platform
from importlib import metadata

STATES = ['AL','AK','AZ','AR','CA','CO','CT','DE','DC','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA',
          'ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR',
          'PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
assert len(STATES) == 51 and len(set(STATES)) == 51
YEAR, HORIZON, SURVEY = '2018', '1-Year', 'person'


def md5_file(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def arrow_type(pa, dtype):
    k = str(dtype)
    if k.startswith('int'):
        return pa.int64()
    if k.startswith('float'):
        return pa.float64()
    if k == 'bool':
        return pa.bool_()
    return pa.string()


def main(outdir):
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    import folktables
    import importlib
    from folktables import ACSDataSource
    load_acs = importlib.import_module('folktables.load_acs')  # the module, not the function of the same name
    os.makedirs(outdir, exist_ok=True)
    rawdir = os.path.join(outdir, 'raw')
    os.makedirs(rawdir, exist_ok=True)
    call = (f"ACSDataSource(survey_year='{YEAR}', horizon='{HORIZON}', survey='{SURVEY}', root_dir='{rawdir}')"
            f".get_data(states={STATES}, download=True)")
    # DC is absent from folktables 0.0.12's lookup tables; add it (same Census URL pattern, csv_pdc.zip)
    load_acs.state_list.append('DC') if 'DC' not in load_acs.state_list else None
    load_acs._STATE_CODES['DC'] = '11'
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            df = ACSDataSource(survey_year=YEAR, horizon=HORIZON, survey=SURVEY,
                               root_dir=rawdir).get_data(states=STATES, download=True)
    except BaseException:
        with open(os.path.join(outdir, 'REFUSAL.txt'), 'w') as f:
            f.write('command:\n' + call + '\n\nfolktables stdout:\n' + buf.getvalue() +
                    '\nerror:\n' + traceback.format_exc())
        print('download or read failed; see REFUSAL.txt')
        sys.exit(2)
    with open(os.path.join(outdir, 'folktables_stdout.txt'), 'w') as f:
        f.write(buf.getvalue())
    base = f'https://www2.census.gov/programs-surveys/acs/data/pums/{YEAR}/{HORIZON}'
    manifest = []
    for s in STATES:
        fips = load_acs._STATE_CODES[s]
        name = f'psam_p{fips}.csv'
        p = os.path.join(rawdir, YEAR, HORIZON, name)
        with open(p, 'rb') as fh:
            nlines = sum(1 for _ in fh)
        manifest.append({'state': s, 'fips': fips, 'file': f'raw/{YEAR}/{HORIZON}/{name}',
                         'url': f'{base}/csv_p{s.lower()}.zip', 'bytes': os.path.getsize(p),
                         'md5': md5_file(p), 'data_rows_in_csv': nlines - 1})
    assert sum(m['data_rows_in_csv'] for m in manifest) == len(df), (sum(m['data_rows_in_csv'] for m in manifest), len(df))
    with open(os.path.join(outdir, 'raw_manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=1)
    fields = [pa.field(c, arrow_type(pa, df[c].dtype)) for c in df.columns]
    schema = pa.schema(fields)
    table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)
    pq.write_table(table, os.path.join(outdir, 'acs_pums2018_all_columns.parquet'), compression='zstd')
    info = {'call': call, 'folktables_version': metadata.version('folktables'),
            'pandas_version': pd.__version__, 'pyarrow_version': pa.__version__,
            'python': platform.python_version(), 'n_rows': int(len(df)), 'n_columns': int(df.shape[1]),
            'columns': [{'name': c, 'dtype': str(df[c].dtype), 'arrow_type': str(schema.field(c).type)} for c in df.columns],
            'dc_note': 'DC added to folktables.load_acs.state_list and _STATE_CODES in memory (absent in 0.0.12)',
            'reader_note': "folktables' reader removes spaces from each data line; raw csv files on disk are untouched"}
    with open(os.path.join(outdir, 'fetch_info.json'), 'w') as f:
        json.dump(info, f, indent=1)
    print('rows', len(df), 'columns', df.shape[1], 'files', len(manifest))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('usage: acs_pums2018_fetch.py OUTDIR')
    main(sys.argv[1])
