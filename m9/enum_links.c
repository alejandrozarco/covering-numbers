/* enum_links.c -- enumerate optimal 2-(n, k, 1) coverings with b blocks in the
 * "dual" representation, as input for isomorph rejection (classify_links.py).
 *
 * A 2-(n,k,1) covering with b blocks (each of size exactly k) is an n x b
 * 0/1 matrix: row q = point q, given as the set S_q of blocks containing q.
 * Conditions:
 *   (a) every pair of points shares a block       <=> the S_q pairwise intersect
 *   (b) every block has exactly k points           <=> column sums = k
 *   (c) |S_q| >= smin  (smin = ceil((n-1)/(k-1)); forced by covering the n-1
 *       pairs through q with blocks that each cover k-1 of them)
 *   (d) blocks are distinct                         <=> columns pairwise distinct
 * Points are unlabelled, so a covering is a MULTISET of n masks.  We list
 * multisets as nondecreasing sequences under key(mask) = (popcount, value).
 * Partial symmetry reduction (sound): some point has |S_q| = smin (because
 * sum |S_q| = b*k and at least one row must be minimal -- checked by caller via
 * the counting argument; we ALSO enumerate without this assumption if
 * smin_forced == 0).  Applying a block permutation we may assume that this
 * set is {0,..,smin-1}, which is the key-minimal mask of popcount smin, hence
 * the first element of the sorted sequence.
 * Output: one line per multiset, n masks in decimal.
 * usage: enum_links n b k smin fix_first(0/1)
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static int n, b, k, smin, fixfirst;
static int cand[1<<16], ncand;
static int seq[64];
static int colsum[16];
static long long leaves = 0;

static int key_less(int x, int y) {
    int px = __builtin_popcount(x), py = __builtin_popcount(y);
    if (px != py) return px < py;
    return x < y;
}

static void dfs(int depth, int start, int total) {
    if (depth == n) {
        for (int c = 0; c < b; c++) if (colsum[c] != k) return;
        /* distinct columns */
        for (int c1 = 0; c1 < b; c1++)
            for (int c2 = c1 + 1; c2 < b; c2++) {
                int same = 1;
                for (int i = 0; i < n && same; i++)
                    if (((seq[i] >> c1) & 1) != ((seq[i] >> c2) & 1)) same = 0;
                if (same) return;
            }
        leaves++;
        for (int i = 0; i < n; i++) printf("%d%c", seq[i], i == n - 1 ? '\n' : ' ');
        return;
    }
    int rem = n - depth;
    for (int ci = start; ci < ncand; ci++) {
        int m = cand[ci];
        int pc = __builtin_popcount(m);
        /* all remaining rows have popcount >= pc (nondecreasing key) */
        if (total + pc * rem > b * k) break;          /* popcounts only grow */
        if (total + b * rem < b * k) return;          /* cannot reach total */
        int ok = 1;
        for (int i = 0; i < depth; i++) if ((seq[i] & m) == 0) { ok = 0; break; }
        if (!ok) continue;
        for (int c = 0; c < b; c++) if ((m >> c) & 1) if (colsum[c] + 1 > k) { ok = 0; break; }
        if (!ok) continue;
        for (int c = 0; c < b; c++) if ((m >> c) & 1) colsum[c]++;
        /* each column must still be completable: k - colsum <= rem-1 */
        int feas = 1;
        for (int c = 0; c < b; c++) if (k - colsum[c] > rem - 1) { feas = 0; break; }
        if (feas) { seq[depth] = m; dfs(depth + 1, ci, total + pc); }
        for (int c = 0; c < b; c++) if ((m >> c) & 1) colsum[c]--;
    }
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: n b k smin fixfirst\n"); return 1; }
    n = atoi(argv[1]); b = atoi(argv[2]); k = atoi(argv[3]); smin = atoi(argv[4]); fixfirst = atoi(argv[5]);
    ncand = 0;
    for (int m = 1; m < (1 << b); m++) if (__builtin_popcount(m) >= smin) cand[ncand++] = m;
    /* insertion sort by key */
    for (int i = 1; i < ncand; i++) { int x = cand[i], j = i - 1; while (j >= 0 && key_less(x, cand[j])) { cand[j + 1] = cand[j]; j--; } cand[j + 1] = x; }
    if (fixfirst) {
        int m = (1 << smin) - 1;
        if (cand[0] != m) { fprintf(stderr, "unexpected order\n"); return 1; }
        seq[0] = m;
        for (int c = 0; c < b; c++) if ((m >> c) & 1) colsum[c]++;
        dfs(1, 0, smin);
    } else {
        dfs(0, 0, 0);
    }
    fprintf(stderr, "leaves %lld\n", leaves);
    return 0;
}
