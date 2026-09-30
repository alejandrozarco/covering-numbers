/* Tiny dense Phase-I simplex:  is { w >= 0 : A w <= b } nonempty?
   A is m x n row-major (n <= 32, m <= 128).  Returns 1 feasible, 0 infeasible.
   On infeasibility, y (length m) receives Farkas-type multipliers y >= 0 (approx.) with
   y^T A >= 0 (componentwise, since w >= 0) and y^T b < 0.  Bland's rule, tolerance 1e-9. */
#include <string.h>
#include <math.h>
#define EPS 1e-9
int lp_feasible(int n, int m, const double *A, const double *b, double *y) {
    /* variables: w (n), slack s (m), artificial a (m).  rows: sign_i*(A_i w + s_i) = |b_i| ; for rows
       with b_i >= 0 the slack is basic, else the artificial is basic (row negated). */
    static double T[130][300]; static int basis[130];
    int cols = n + 2 * m, i, j, r, c;
    if (m > 128 || cols + 1 > 300) return -1;
    for (i = 0; i < m; i++) {
        double sg = b[i] >= 0 ? 1.0 : -1.0;
        for (j = 0; j < cols + 1; j++) T[i][j] = 0.0;
        for (j = 0; j < n; j++) T[i][j] = sg * A[i * n + j];
        T[i][n + i] = sg;
        T[i][cols] = sg * b[i];
        if (sg > 0) basis[i] = n + i; else { T[i][n + m + i] = 1.0; basis[i] = n + m + i; }
    }
    /* objective row: minimise sum of artificials -> reduced costs */
    double *z = T[m];
    for (j = 0; j < cols + 1; j++) z[j] = 0.0;
    for (i = 0; i < m; i++) if (basis[i] >= n + m) for (j = 0; j < cols + 1; j++) z[j] -= T[i][j];
    for (i = 0; i < m; i++) if (basis[i] >= n + m) z[basis[i]] = 0.0;
    for (int it = 0; it < 5000; it++) {
        c = -1;
        for (j = 0; j < cols; j++) if (z[j] < -EPS) { c = j; break; }   /* Bland */
        if (c < 0) break;
        r = -1; double best = 0;
        for (i = 0; i < m; i++) if (T[i][c] > EPS) {
            double q = T[i][cols] / T[i][c];
            if (r < 0 || q < best - 1e-12 || (fabs(q - best) <= 1e-12 && basis[i] < basis[r])) { r = i; best = q; }
        }
        if (r < 0) break; /* unbounded direction in phase I cannot happen */
        double pv = T[r][c];
        for (j = 0; j < cols + 1; j++) T[r][j] /= pv;
        for (i = 0; i <= m; i++) if (i != r && fabs(T[i][c]) > 0) {
            double f = T[i][c];
            for (j = 0; j < cols + 1; j++) T[i][j] -= f * T[r][j];
        }
        basis[r] = c;
    }
    double infeas = -z[cols];
    if (infeas <= 1e-7) return 1;
    /* Farkas multipliers: y_i = reduced cost of slack i  (dual of phase I), clipped at 0 */
    if (y) for (i = 0; i < m; i++) { double v = z[n + i]; y[i] = v > 0 ? v : 0.0; }
    return 0;
}
