/* Fast theory oracle for the Key Lemma CDCL(T) search (floating point; used only to FIND lemmas —
   every lemma is later certified by an exact rational Farkas certificate and checked independently).
   Assignment: X[i*14+j] in {-1 (unassigned), 0, 1}; C4[k] (|S0∩Sk|>=4 ?) and T3[k] in {-1,0,1}.
   Constraints on w >= 0 (R vars): w_i <= 1/8; sum w = 1; w_k <= w_0 (k>=1);
   U(j): sum_{X[i][j]=1} w_i <= 1/2 ; D(j): sum_{X[i][j]!=0} w_i >= 1/2 ;
   C4[k]=0 (k>=2): w_k <= w_1 ;  T3[k]=1 (k>=3, if use_t3): w_k <= w_2. */
#include <string.h>
#include <math.h>
#define EPS 1e-9
#define MAXR 16
#define MAXM 96
#define MAXC (MAXR + 2*MAXM + 1)
static int use_avoid0;
static double T[MAXM + 1][MAXC]; static int basis[MAXM];
static double A[MAXM][MAXR], B[MAXM]; static int rtype[MAXM], ridx[MAXM]; static int last_m;
static int phase1(int n, int m) {
    int cols = n + 2 * m, i, j, r, c;
    for (i = 0; i < m; i++) {
        double sg = B[i] >= 0 ? 1.0 : -1.0;
        memset(T[i], 0, sizeof(double) * (cols + 1));
        for (j = 0; j < n; j++) T[i][j] = sg * A[i][j];
        T[i][n + i] = sg; T[i][cols] = sg * B[i];
        if (sg > 0) basis[i] = n + i; else { T[i][n + m + i] = 1.0; basis[i] = n + m + i; }
    }
    double *z = T[m]; memset(z, 0, sizeof(double) * (cols + 1));
    for (i = 0; i < m; i++) if (basis[i] >= n + m) for (j = 0; j <= cols; j++) z[j] -= T[i][j];
    for (i = 0; i < m; i++) if (basis[i] >= n + m) z[basis[i]] = 0.0;
    for (int it = 0; it < 20000; it++) {
        c = -1; double mn = -EPS;
        if (it < 2000) { for (j = 0; j < cols; j++) if (z[j] < mn) { mn = z[j]; c = j; } }   /* Dantzig */
        else { for (j = 0; j < cols; j++) if (z[j] < -EPS) { c = j; break; } }            /* Bland */
        if (c < 0) break;
        r = -1; double best = 0;
        for (i = 0; i < m; i++) if (T[i][c] > EPS) {
            double q = T[i][cols] / T[i][c];
            if (r < 0 || q < best - 1e-12 || (fabs(q - best) <= 1e-12 && basis[i] < basis[r])) { r = i; best = q; }
        }
        if (r < 0) break;
        double pv = T[r][c];
        for (j = 0; j <= cols; j++) T[r][j] /= pv;
        for (i = 0; i <= m; i++) if (i != r && T[i][c] != 0.0) {
            double f = T[i][c];
            for (j = 0; j <= cols; j++) T[i][j] -= f * T[r][j];
        }
        basis[r] = c;
    }
    return (-z[cols]) <= 1e-7;   /* 1 = feasible */
}
static int build(int R, const signed char *X, const signed char *C4, const signed char *T3) {
    int m = 0, i, j;
    for (i = 0; i < R; i++) { memset(A[m], 0, sizeof(double) * R); A[m][i] = 1; rtype[m] = 0; B[m++] = 0.125; }
    memset(A[m], 0, sizeof(double) * R); for (i = 0; i < R; i++) A[m][i] = 1; rtype[m] = 0; B[m++] = 1;
    memset(A[m], 0, sizeof(double) * R); for (i = 0; i < R; i++) A[m][i] = -1; rtype[m] = 0; B[m++] = -1;
    for (i = 1; i < R; i++) { memset(A[m], 0, sizeof(double) * R); A[m][i] = 1; A[m][0] = -1; rtype[m] = 0; B[m++] = 0; }
    for (j = 0; j < 14; j++) {
        int np = 0, nq = 0;
        for (i = 0; i < R; i++) { if (X[i * 14 + j] == 1) np++; if (X[i * 14 + j] != 0) nq++; }
        if (np) { memset(A[m], 0, sizeof(double) * R); for (i = 0; i < R; i++) if (X[i*14+j] == 1) A[m][i] = 1; rtype[m] = 1; ridx[m] = j; B[m++] = 0.5; }
        if (nq < R) { memset(A[m], 0, sizeof(double) * R); for (i = 0; i < R; i++) if (X[i*14+j] != 0) A[m][i] = -1; rtype[m] = 2; ridx[m] = j; B[m++] = -0.5; }
    }
    for (i = 2; i < R; i++) if (C4[i] == 0) { memset(A[m], 0, sizeof(double) * R); A[m][i] = 1; A[m][1] = -1; rtype[m] = 3; ridx[m] = i; B[m++] = 0; }
    if (use_avoid0) for (i = 4; i < R; i++) if (X[i*14] == 0) { memset(A[m], 0, sizeof(double) * R); A[m][i] = 1; A[m][3] = -1; rtype[m] = 5; ridx[m] = i; B[m++] = 0; }
    for (i = 3; i < R; i++) if (T3[i] == 1) { memset(A[m], 0, sizeof(double) * R); A[m][i] = 1; A[m][2] = -1; rtype[m] = 4; ridx[m] = i; B[m++] = 0; }
    return m;
}
void set_avoid0(int v) { use_avoid0 = v; }
int infeasible(int R, const signed char *X, const signed char *C4, const signed char *T3) {
    int m = build(R, X, C4, T3); last_m = m;
    return !phase1(R, m);
}
/* deletion-based minimisation of an infeasible assignment (in place): tries to unassign each
   assigned entry (x entries column by column first as whole columns, then singly, then C4, T3). */
int minimize(int R, signed char *X, signed char *C4, signed char *T3) {
    signed char sv[14 * MAXR]; int i, j;
    if (!infeasible(R, X, C4, T3)) return 0;
    {   /* keep only literals occurring in rows with nonzero phase-1 dual (reduced cost of their slack) */
        int m = last_m, cols = R + 2 * m; double *z = T[m];
        signed char keepX[14 * MAXR], keepC[MAXR], keepT[MAXR];
        memset(keepX, 0, sizeof keepX); memset(keepC, 0, sizeof keepC); memset(keepT, 0, sizeof keepT);
        (void)cols;
        for (int r = 0; r < m; r++) if (fabs(z[R + r]) > 1e-9) {
            if (rtype[r] == 1) { for (i = 0; i < R; i++) if (X[i*14 + ridx[r]] == 1) keepX[i*14 + ridx[r]] = 1; }
            else if (rtype[r] == 2) { for (i = 0; i < R; i++) if (X[i*14 + ridx[r]] == 0) keepX[i*14 + ridx[r]] = 1; }
            else if (rtype[r] == 3) keepC[ridx[r]] = 1;
            else if (rtype[r] == 4) keepT[ridx[r]] = 1;
            else if (rtype[r] == 5) keepX[ridx[r]*14] = 1;
        }
        signed char X2[14 * MAXR], C2[MAXR], T2[MAXR];
        for (i = 0; i < R * 14; i++) X2[i] = keepX[i] ? X[i] : -1;
        for (i = 0; i < R; i++) { C2[i] = keepC[i] ? C4[i] : -1; T2[i] = keepT[i] ? T3[i] : -1; }
        if (infeasible(R, X2, C2, T2)) { memcpy(X, X2, R * 14); memcpy(C4, C2, R); memcpy(T3, T2, R); }
    }
    for (j = 0; j < 14; j++) {           /* whole columns */
        for (i = 0; i < R; i++) { sv[i] = X[i*14+j]; X[i*14+j] = -1; }
        if (!infeasible(R, X, C4, T3)) for (i = 0; i < R; i++) X[i*14+j] = sv[i];
    }
    for (i = 0; i < R * 14; i++) if (X[i] != -1) {
        signed char s = X[i]; X[i] = -1; if (!infeasible(R, X, C4, T3)) X[i] = s;
    }
    for (i = 0; i < R; i++) if (C4[i] != -1) { signed char s = C4[i]; C4[i] = -1; if (!infeasible(R, X, C4, T3)) C4[i] = s; }
    for (i = 0; i < R; i++) if (T3[i] != -1) { signed char s = T3[i]; T3[i] = -1; if (!infeasible(R, X, C4, T3)) T3[i] = s; }
    return 1;
}
