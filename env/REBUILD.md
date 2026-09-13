# Pinned rebuild recipe — HEST replication

Canonical build for this project. TRIDENT is an UNPINNED git dependency in HEST's
`pyproject.toml`; encoder transforms have changed between TRIDENT versions, which would
shift Pearson values without raising an error. Always install with the pin below.

- HEST commit   : `3ddb5eaf5bd2a8133e0c0e8015816489a3d99dc3`
- TRIDENT commit: `f3eb7f301ce34f875306b545e6cfefc5d3335a5c`
- python        : Python 3.11.16
- built         : 2026-09-13T16:35:35-04:00

## Rebuild

```bash
ROOT=/work/users/w/e/weiyang/hest_replication
source $ROOT/env/miniforge3/etc/profile.d/conda.sh
conda create -y -n hest python=3.11
conda activate hest
conda install -y -c conda-forge libvips pyvips openslide openslide-python libffi

git -C $ROOT/code/HEST checkout 3ddb5eaf5bd2a8133e0c0e8015816489a3d99dc3
cd $ROOT/code/HEST
pip install -e .
pip install -e ".[benchmark]"

# PIN TRIDENT (must come after the HEST installs, which would otherwise float it)
pip install --force-reinstall --no-deps \
  "trident @ git+https://github.com/mahmoodlab/TRIDENT.git@f3eb7f301ce34f875306b545e6cfefc5d3335a5c"

python -c "import hest, trident; print('ok')"
```

Exact versions of every package: `env/requirements.lock` · conda: `env/conda_env.yaml`
