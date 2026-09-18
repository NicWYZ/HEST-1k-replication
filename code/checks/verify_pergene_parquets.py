import glob, pyarrow.parquet as pq
fs = sorted(glob.glob('/work/users/w/e/weiyang/hest_replication/results/round2/R3_splits/pergene__*.parquet'))
EXP = ['blocked','blocked_buffered','blocked_matched','patient','random','random_matched','slide_out']
for f in fs:
    t = pq.read_table(f).to_pandas()
    dt = dict((n, str(d)) for n, d in zip(t.columns, t.dtypes))
    so = t[t.design == 'slide_out']
    print('%-28s rows=%d designs=%d/%d tasks=%d genes=%d pearson_nulls=%d '
          'fold=%s grid=%s fold_eq_slide=%s zeropad=%s'
          % (f.split('/')[-1], len(t), t.design.nunique(), len(EXP), t.task.nunique(),
             t.gene.nunique(), int(t.pearson.isna().sum()), dt['fold'], dt['grid'],
             bool((so.fold == so.slide).all()),
             bool(t[t.design != 'slide_out'].fold.str.fullmatch(r'\d{2}').all())))
    assert sorted(t.design.unique()) == EXP, f
    assert int(t.pearson.isna().sum()) == 0, f
print('ALL THREE PASS')
