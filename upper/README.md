# New upper bounds from weighted blow-ups of finite geometries

Status: AI-produced, not peer reviewed; see [`AI_DISCLOSURE.md`](../AI_DISCLOSURE.md). Each covering is checked by
`scripts/check_covering.py`.

| covering | best previously listed (coveringrepository.com, 2026-09-30) | construction |
|---|---|---|
| `C45_23_5_b63.txt` — $C(45,23,5) \le 63$ | 65 (J. de Heer, S. Muir, 2014) | 45 of the 63 points of $\mathrm{PG}(5,2)$, chosen so that every hyperplane contains at most 23 of them; blocks = the 63 hyperplanes (padded to 23 points) |
| `C44_24_6_b126.txt` — $C(44,24,6) \le 126$ | 128 (F. Atzeni, 2024) | 43 points of $\mathrm{AG}(6,2)$, one of them doubled (44 points); blocks = the 126 affine hyperplanes (at most 24 points each, padded to 24) |

Why they work: any 5 points of $\mathrm{PG}(5,2)$ lie in a common hyperplane, and any 6 points of $\mathrm{AG}(6,2)$ lie in a
common affine hyperplane. So if each geometric point is replaced by $w_x \ge 0$ new points, with $\sum w_x = v$ and every
hyperplane carrying at most $k$ new points, the hyperplanes give a $(v,k,t)$ covering. The weights were found by integer
programming (`blowscan.py`, which scans such blow-ups of 28 structures against the LJCR v1.2 data).

Added 2026-10-07 (scan `blowscan2.py`, coverings rebuilt by `python3 upper/build_blowup.py upper/blowscan2_hits.jsonl INDEX out.txt` from the recorded weights; best listed
values read on coveringrepository.com on 2026-10-07):

| covering | best previously listed | construction |
|---|---|---|
| `C54_19_4_b121.txt` — $C(54,19,4) \le 121$ | 128 (F. Atzeni, 2024) | hyperplanes of $\mathrm{PG}(4,3)$, 54 of its 121 points |
| `C55_19_4_b121.txt` — $C(55,19,4) \le 121$ | 131 (F. Atzeni, 2025) | hyperplanes of $\mathrm{PG}(4,3)$, 55 points |
| `C65_23_4_b121.txt` — $C(65,23,4) \le 121$ | 128 (F. Atzeni, 2024) | hyperplanes of $\mathrm{PG}(4,3)$, some points doubled |
| `C69_24_4_b121.txt` — $C(69,24,4) \le 121$ | 125 (F. Atzeni, 2024) | hyperplanes of $\mathrm{PG}(4,3)$, some points doubled |
| `C64_14_3_b156.txt` — $C(64,14,3) \le 156$ | 162 (F. Atzeni, 2025) | planes of $\mathrm{PG}(3,5)$, some points doubled |
| `C76_16_3_b156.txt` — $C(76,16,3) \le 156$ | 167 (F. Atzeni, 2025) | planes of $\mathrm{PG}(3,5)$ |
| `C95_20_3_b155.txt` — $C(95,20,3) \le 155$ | 160 (J. de Heer, S. Muir, 2014) | planes of $\mathrm{AG}(3,5)$, some points doubled |

Any 4 points of $\mathrm{PG}(4,3)$ lie in a hyperplane, and any 3 points of $\mathrm{PG}(3,5)$ or $\mathrm{AG}(3,5)$ lie in a
plane, so the same blow-up argument applies. An independent AI review (gpt-6-astra) re-checked every $t$-subset of all
seven files with its own program and the construction argument: `review_astra_2026-10-07.md`.

Check (points are numbered from 0; one block per line):

```sh
python3 scripts/check_covering.py 45 23 5 upper/C45_23_5_b63.txt
python3 scripts/check_covering.py 44 24 6 upper/C44_24_6_b126.txt
python3 scripts/check_covering.py 54 19 4 upper/C54_19_4_b121.txt
python3 scripts/check_covering.py 55 19 4 upper/C55_19_4_b121.txt
python3 scripts/check_covering.py 65 23 4 upper/C65_23_4_b121.txt
python3 scripts/check_covering.py 69 24 4 upper/C69_24_4_b121.txt
python3 scripts/check_covering.py 64 14 3 upper/C64_14_3_b156.txt
python3 scripts/check_covering.py 76 16 3 upper/C76_16_3_b156.txt
python3 scripts/check_covering.py 95 20 3 upper/C95_20_3_b155.txt
```
