# New upper bounds from weighted blow-ups of finite geometries

| covering | best previously listed (coveringrepository.com, 2026-09-30) | construction |
|---|---|---|
| `C45_23_5_b63.txt` — $C(45,23,5) \le 63$ | 65 (J. de Heer, S. Muir, 2014) | 45 of the 63 points of $\mathrm{PG}(5,2)$, chosen so that every hyperplane contains at most 23 of them; blocks = the 63 hyperplanes (padded to 23 points) |
| `C44_24_6_b126.txt` — $C(44,24,6) \le 126$ | 128 (F. Atzeni, 2024) | 43 points of $\mathrm{AG}(6,2)$, one of them doubled (44 points); blocks = the 126 affine hyperplanes (at most 24 points each, padded to 24) |

Why they work: any 5 points of $\mathrm{PG}(5,2)$ lie in a common hyperplane, and any 6 points of $\mathrm{AG}(6,2)$ lie in a
common affine hyperplane. So if each geometric point is replaced by $w_x \ge 0$ new points, with $\sum w_x = v$ and every
hyperplane carrying at most $k$ new points, the hyperplanes give a $(v,k,t)$ covering. The weights were found by integer
programming (`blowscan.py`, which scans such blow-ups of 28 structures against the LJCR v1.2 data).

Check (points are numbered from 0; one block per line):

```sh
python3 scripts/check_covering.py 45 23 5 upper/C45_23_5_b63.txt
python3 scripts/check_covering.py 44 24 6 upper/C44_24_6_b126.txt
```
