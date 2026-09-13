# MANIFEST — large artifacts held on Longleaf

Generated: 2026-09-13T16:38:21
Host path root: `/work/users/w/e/weiyang/hest_replication`

These files are deliberately **not** committed: GitHub's 100 MB per-file limit, and
`MahmoodLab/hest-bench` is a gated dataset (`inference_dump.pkl` contains `targets_all`,
the measured expression). Hashes let a collaborator verify a copy obtained through
proper channels.

## `bench_data/`

hest-bench snapshot (GATED - MahmoodLab/hest-bench)

- files: 887
- total size: 39.1 GB

## `embeddings/`

per-encoder per-sample patch embeddings (HDF5)

- files: 140
- total size: 1.8 GB

## `instrumentation/`

Stage 4 joined tables

- files: 1
- total size: 795.0 B

## Per-split inference dumps

| path (relative to root) | size | sha256 |
|---|---|---|
| `results/faithful/faithful_pca_ridge__conch_v1::26-09-13-16-30-44/IDC/conch_v1/split0/inference_dump.pkl` | 15.8 MB | `9bb2bea5497023add54721dbd98dee1ae50fdf00d20ec383a458d62ba2559365` |
| `results/faithful/faithful_pca_ridge__conch_v1::26-09-13-16-30-44/IDC/conch_v1/split1/inference_dump.pkl` | 5.9 MB | `ae70ce3120661a8b9493a851149461cca3ad7f4998f3aaa51c5ac2ad1a69844e` |
| `results/faithful/faithful_pca_ridge__conch_v1::26-09-13-16-30-44/IDC/conch_v1/split2/inference_dump.pkl` | 3.1 MB | `ba3eee3f0a45827f426b6bda9d0d30c5154be1f6fa563df11b0f84fbc81f7e17` |
| `results/faithful/faithful_pca_ridge__conch_v1::26-09-13-16-30-44/IDC/conch_v1/split3/inference_dump.pkl` | 2.3 MB | `0acf736952db1e2e7695be20e613479c8067c499358ecaf151d421453c91d554` |
| `results/faithful/faithful_pca_ridge__ctranspath::26-09-13-16-30-55/IDC/ctranspath/split0/inference_dump.pkl` | 15.8 MB | `d13438932305c889e81fcf7c53194e5e52c0b6b2bad20083688003f85c1d2321` |
| `results/faithful/faithful_pca_ridge__ctranspath::26-09-13-16-30-55/IDC/ctranspath/split1/inference_dump.pkl` | 5.9 MB | `7a968e6dd4b4f27d83df00228bc6423f21e61c39ae2335117e69f8e2b007bdd1` |
| `results/faithful/faithful_pca_ridge__ctranspath::26-09-13-16-30-55/IDC/ctranspath/split2/inference_dump.pkl` | 3.1 MB | `716e52f6eba20d2a8bc73e8e358db1c284e3ba3826c57aafcd581d1852aaccf0` |
| `results/faithful/faithful_pca_ridge__ctranspath::26-09-13-16-30-55/IDC/ctranspath/split3/inference_dump.pkl` | 2.3 MB | `de8b9539ca34f321495d20a6db9cc04b54da3251f1b7551910e95ddd5fc5dc9c` |
| `results/faithful/faithful_pca_ridge__gigapath::26-09-13-16-30-32/IDC/gigapath/split0/inference_dump.pkl` | 15.8 MB | `953b2d8f99820459f6c3465b6591e6bd2b0cbc22c445c0f02a9cf5fc3f641ec6` |
| `results/faithful/faithful_pca_ridge__gigapath::26-09-13-16-30-32/IDC/gigapath/split1/inference_dump.pkl` | 5.9 MB | `2b172fa60949f7c3022253d568443ccb6b3926b6220b4c33d0a812a0ed35fe85` |
| `results/faithful/faithful_pca_ridge__gigapath::26-09-13-16-30-32/IDC/gigapath/split2/inference_dump.pkl` | 3.1 MB | `6c5ded8d3156e4c045a510787f5cd8b83375d8d5908b3300095a34fbf1c59fd4` |
| `results/faithful/faithful_pca_ridge__gigapath::26-09-13-16-30-32/IDC/gigapath/split3/inference_dump.pkl` | 2.3 MB | `8bf5ea7d3553f090bb475e19cca94842aff893df87946a4f3f1defcf141a8d54` |
| `results/faithful/faithful_pca_ridge__phikon::26-09-13-16-30-45/IDC/phikon/split0/inference_dump.pkl` | 15.8 MB | `b47a41f7e0a09fa1aed85c6bb76619335691f287373150a12fa806a09730aea9` |
| `results/faithful/faithful_pca_ridge__phikon::26-09-13-16-30-45/IDC/phikon/split1/inference_dump.pkl` | 5.9 MB | `bbc8e85930e6b609bc9bf14db4e402791070bc76761b5e46058509d9b7066c70` |
| `results/faithful/faithful_pca_ridge__phikon::26-09-13-16-30-45/IDC/phikon/split2/inference_dump.pkl` | 3.1 MB | `62addaa661033f02048592b1289b64e76f41b1231a6ce0275f73b549630aa3c0` |
| `results/faithful/faithful_pca_ridge__phikon::26-09-13-16-30-45/IDC/phikon/split3/inference_dump.pkl` | 2.3 MB | `388f769a8f179e32e4816fdb391d9eb4715ca6191e9b52fc5740052af68ce8ad` |
| `results/faithful/faithful_pca_ridge__phikon::26-09-13-16-30-45/PRAD/phikon/split0/inference_dump.pkl` | 19.8 MB | `5b2e6f0d0ee8fce58695312b3ebcd2545736d8de0f4a86bbc712ba1f71bf2c9a` |
| `results/faithful/faithful_pca_ridge__phikon::26-09-13-16-30-45/PRAD/phikon/split1/inference_dump.pkl` | 28.1 MB | `4bfff8f2683e89c0c9c89def1780acf30cc151c0f253349677c209f39e74a449` |
| `results/faithful/faithful_pca_ridge__resnet50::26-09-13-16-30-55/IDC/resnet50/split0/inference_dump.pkl` | 15.8 MB | `337eeda23edb43baa9b0e9892c33ae34d98a09a1bca75db3508efb629bbf183f` |
| `results/faithful/faithful_pca_ridge__resnet50::26-09-13-16-30-55/IDC/resnet50/split1/inference_dump.pkl` | 5.9 MB | `51a12025211fcc79b7d595fb6f5d85e719ab9b7bae92dd7e84796b063f4abf08` |
| `results/faithful/faithful_pca_ridge__resnet50::26-09-13-16-30-55/IDC/resnet50/split2/inference_dump.pkl` | 3.1 MB | `b31ccd3a048b11e275b20df9f1d72dab13a4ce1ca2bc2fd721f7f91a84140fd1` |
| `results/faithful/faithful_pca_ridge__resnet50::26-09-13-16-30-55/IDC/resnet50/split3/inference_dump.pkl` | 2.3 MB | `683c5a07df1cae8e1a57277025ca6d9b6c43edc844afc036a695f2b3d909e27e` |
| `results/faithful/faithful_pca_ridge__resnet50::26-09-13-16-30-55/PAAD/resnet50/split0/inference_dump.pkl` | 1.5 MB | `dc1e51d0e80fc74a806f382ecea8594a7b2f8fc68e52ac670579b937d8710782` |
| `results/faithful/faithful_pca_ridge__resnet50::26-09-13-16-30-55/PAAD/resnet50/split1/inference_dump.pkl` | 2.8 MB | `17b759a7b20d0f13db47817a2a92c3b5590e56a667d3bd5d7942cfe0eb72e7da` |
| `results/faithful/faithful_pca_ridge__resnet50::26-09-13-16-30-55/PAAD/resnet50/split2/inference_dump.pkl` | 1.5 MB | `6ce188b7d1d8f1f57934e255eac8c9714f9e3e50df5eb43fab1f3836cbc436d5` |
| `results/faithful/faithful_pca_ridge__resnet50::26-09-13-16-30-55/PRAD/resnet50/split0/inference_dump.pkl` | 19.8 MB | `69f3abf140b1fbdc704c0bccb9f7ad445a5bb6812634d735285628ea32be1dd3` |
| `results/faithful/faithful_pca_ridge__resnet50::26-09-13-16-30-55/PRAD/resnet50/split1/inference_dump.pkl` | 28.1 MB | `7b0b78ef71b55e5c8466acfbf1c335901649fcbb18d1c452f5fad789f159f1d7` |
| `results/faithful/faithful_pca_ridge__resnet50::26-09-13-16-30-55/SKCM/resnet50/split0/inference_dump.pkl` | 1010.4 KB | `0ea6486a2852c0b9ddcff4222d84ffa3be729abc3b9a5a903b9ec0d6f781e1a4` |
| `results/faithful/faithful_pca_ridge__resnet50::26-09-13-16-30-55/SKCM/resnet50/split1/inference_dump.pkl` | 1.3 MB | `05a85c3a5a464a94557c4e067a72fb8db616961f37a531cbdd1736622987f0a2` |
| `results/faithful/faithful_pca_ridge__uni_v1::26-09-13-16-30-32/IDC/uni_v1/split0/inference_dump.pkl` | 15.8 MB | `e16383636a078286a353cc50fde28a4590b5b71f75aed29c0e0aac83cb2a6115` |
| `results/faithful/faithful_pca_ridge__uni_v1::26-09-13-16-30-32/IDC/uni_v1/split1/inference_dump.pkl` | 5.9 MB | `d3ec857dee3c0b8cad74100e6238926921d9c099003cf9e6418e4168ddd05759` |
| `results/faithful/faithful_pca_ridge__uni_v1::26-09-13-16-30-32/IDC/uni_v1/split2/inference_dump.pkl` | 3.1 MB | `6d530ecf9990dd045af806619cfdfc98544d86801e7442d09325dc39bd872ac6` |
| `results/faithful/faithful_pca_ridge__uni_v1::26-09-13-16-30-32/IDC/uni_v1/split3/inference_dump.pkl` | 2.3 MB | `69c1da0dc2edd15aa36554e1c857d35055cb8c30d11cbe4938976167390f5981` |
| `results/faithful/faithful_pca_ridge__uni_v1::26-09-13-16-30-32/PRAD/uni_v1/split0/inference_dump.pkl` | 19.8 MB | `c52fd859bf02acb3a81febfe8bfcdda691260438b32d7afef6e855165be7b8f8` |
| `results/faithful/faithful_pca_ridge__uni_v1::26-09-13-16-30-32/PRAD/uni_v1/split1/inference_dump.pkl` | 28.1 MB | `405ce3ea48f8779d7db761674597c00061167a7de2727659a592e48273389bc1` |
| `results/faithful/smoke_resnet50_IDC::26-09-13-14-30-02/IDC/resnet50/split0/inference_dump.pkl` | 15.8 MB | `337eeda23edb43baa9b0e9892c33ae34d98a09a1bca75db3508efb629bbf183f` |
| `results/faithful/smoke_resnet50_IDC::26-09-13-14-30-02/IDC/resnet50/split1/inference_dump.pkl` | 5.9 MB | `51a12025211fcc79b7d595fb6f5d85e719ab9b7bae92dd7e84796b063f4abf08` |
| `results/faithful/smoke_resnet50_IDC::26-09-13-14-30-02/IDC/resnet50/split2/inference_dump.pkl` | 3.1 MB | `b31ccd3a048b11e275b20df9f1d72dab13a4ce1ca2bc2fd721f7f91a84140fd1` |
| `results/faithful/smoke_resnet50_IDC::26-09-13-14-30-02/IDC/resnet50/split3/inference_dump.pkl` | 2.3 MB | `683c5a07df1cae8e1a57277025ca6d9b6c43edc844afc036a695f2b3d909e27e` |

**39 dump files hashed.**

Grand total across all untracked artifacts: 1,067 files, 41.3 GB.
