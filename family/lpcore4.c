/* Floating-point theory oracle for the Key Lemma CDCL(T) search (klprop.py).  Used only to FIND
   lemmas; every lemma is certified afterwards with exact rational Farkas multipliers (klcertify.py)
   and checked independently (klcheck.py).
   Assignment arrays (values -1 = unassigned, 0, 1):
     X[i*14+j]  : row i contains column j
     P[i*R+k]   : |S_i ∩ S_k| >= 4   (i<k, stored symmetrically)
     T3[k]      : rows 0,1,k form a triangle with triple intersection 1   (case A only)
   Constraint rows over w >= 0:
     w_i <= 1/8 ; sum w = 1 (two rows) ; w_k <= w_0 (k>=1)
     U(j):  sum_{X[i][j]=1} w_i <= 1/2          D(j):  sum_{X[i][j]!=0} w_i >= 1/2
     partner(k): w_k <= w_1  if P[0][k]=0 (k>=2)
     third(k):   w_k <= w_2  if T3[k]=1 (k>=3)
     E1(i): sum_{k: P[i][k]=1} w_k + 4 w_i <= 1/2      E2(i): 4 sum_{k: P[i][k]!=0} w_k + 4 w_i >= 1/2 */
#include <string.h>
#include <math.h>
#define EPS 1e-9
#define MAXR 16
#define MAXM 360
#define MAXC (MAXR + 2*MAXM + 1)
static double T[MAXM + 1][MAXC]; static int basis[MAXM];
static double A[MAXM][MAXR], B[MAXM]; static int rtype[MAXM], ridx[MAXM]; static int last_m;
static int use_E = 1, use_F = 0, wsort = 0, minmode = 0;
void set_minmode(int v) { minmode = v; } static double posd = 0.0;
void set_wsort(int v) { wsort = v; }
void set_pos(double d) { posd = d; }
void set_useE(int v) { use_E = v; }
void set_useF(int v) { use_F = v; }
static const signed char *QQ;
#define QI(i,k,l) ((i)*R*R + (k)*R + (l))
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
        if (it < 2000) { for (j = 0; j < cols; j++) if (z[j] < mn) { mn = z[j]; c = j; } }
        else { for (j = 0; j < cols; j++) if (z[j] < -EPS) { c = j; break; } }
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
    return (-z[cols]) <= 1e-7;
}
#define NEWROW(t, x) do { memset(A[m], 0, sizeof(double) * R); rtype[m] = (t); ridx[m] = (x); } while (0)
static int build(int R, const signed char *X, const signed char *P, const signed char *T3) {
    int m = 0, i, j, k, l;
    for (i = 0; i < R; i++) { NEWROW(0, i); A[m][i] = 1; B[m++] = 0.125; }
    NEWROW(0, 0); for (i = 0; i < R; i++) A[m][i] = 1; B[m++] = 1;
    NEWROW(0, 0); for (i = 0; i < R; i++) A[m][i] = -1; B[m++] = -1;
    for (i = 1; i < R; i++) { NEWROW(0, i); A[m][i] = 1; A[m][0] = -1; B[m++] = 0; }
    if (posd > 0) for (i = 0; i < R; i++) { NEWROW(0, i); A[m][i] = -1; B[m++] = -posd; }
    if (wsort) for (i = wsort; i < R - 1; i++) { NEWROW(0, i); A[m][i+1] = 1; A[m][i] = -1; B[m++] = 0; }
    for (j = 0; j < 14; j++) {
        int np = 0, nq = 0;
        for (i = 0; i < R; i++) { if (X[i*14+j] == 1) np++; if (X[i*14+j] != 0) nq++; }
        if (np) { NEWROW(1, j); for (i = 0; i < R; i++) if (X[i*14+j] == 1) A[m][i] = 1; B[m++] = 0.5; }
        if (nq < R) { NEWROW(2, j); for (i = 0; i < R; i++) if (X[i*14+j] != 0) A[m][i] = -1; B[m++] = -0.5; }
    }
    for (k = 2; k < R; k++) if (P[0*R+k] == 0) { NEWROW(3, k); A[m][k] = 1; A[m][1] = -1; B[m++] = 0; }
    for (k = 3; k < R; k++) if (T3[k] == 1) { NEWROW(4, k); A[m][k] = 1; A[m][2] = -1; B[m++] = 0; }
    if (use_E) for (i = 0; i < R; i++) {
        NEWROW(6, i); for (k = 0; k < R; k++) if (k != i && P[i*R+k] == 1) A[m][k] = 1; A[m][i] = 4; B[m++] = 0.5;
        NEWROW(7, i); for (k = 0; k < R; k++) if (k != i && P[i*R+k] != 0) A[m][k] = -4; A[m][i] = -4; B[m++] = -0.5;
    }
    if (use_F) for (i = 0; i < R; i++) for (k = i + 1; k < R; k++) if (P[i*R+k] == 0) {
        NEWROW(8, i*R+k); for (l = 0; l < R; l++) if (l != i && l != k && QQ[QI(i,k,l)] == 1) A[m][l] = 1;
        A[m][i] += 2; A[m][k] += 2; B[m++] = 0.5;
        NEWROW(9, i*R+k); for (l = 0; l < R; l++) if (l != i && l != k && QQ[QI(i,k,l)] != 0) A[m][l] = -2;
        A[m][i] += -2; A[m][k] += -2; B[m++] = -0.5;
    }
    return m;
}
static int infeasible_(int R, const signed char *X, const signed char *P, const signed char *T3) {
    int m = build(R, X, P, T3); last_m = m;
    return !phase1(R, m);
}
int infeasible(int R, const signed char *X, const signed char *P, const signed char *T3, const signed char *Q) { QQ = Q; return infeasible_(R, X, P, T3); }
static void setP(int R, signed char *P, int i, int k, signed char v) { P[i*R+k] = v; P[k*R+i] = v; }
static void setQ(int R, signed char *Q, int i, int k, int l, signed char v) {
    Q[QI(i,k,l)] = Q[QI(i,l,k)] = Q[QI(k,i,l)] = Q[QI(k,l,i)] = Q[QI(l,i,k)] = Q[QI(l,k,i)] = v; }
int minimize(int R, signed char *X, signed char *P, signed char *T3, signed char *Q) {
    signed char sv[14 * MAXR]; int i, j, k, l; QQ = Q;
    if (!infeasible_(R, X, P, T3)) return 0;
    {   int m = last_m; double *z = T[m];
        signed char kX[14*MAXR], kP[MAXR*MAXR], kT[MAXR]; static signed char kQ[MAXR*MAXR*MAXR], Q2[MAXR*MAXR*MAXR];
        memset(kX, 0, sizeof kX); memset(kP, 0, sizeof kP); memset(kT, 0, sizeof kT); memset(kQ, 0, R*R*R);
        for (int r = 0; r < m; r++) if (fabs(z[R + r]) > 1e-9) {
            int t = rtype[r], x = ridx[r];
            if (t == 1) { for (i = 0; i < R; i++) if (X[i*14+x] == 1) kX[i*14+x] = 1; }
            else if (t == 2) { for (i = 0; i < R; i++) if (X[i*14+x] == 0) kX[i*14+x] = 1; }
            else if (t == 3) { kP[0*R+x] = kP[x*R+0] = 1; }
            else if (t == 4) kT[x] = 1;
            else if (t == 6) { for (k = 0; k < R; k++) if (k != x && P[x*R+k] == 1) kP[x*R+k] = kP[k*R+x] = 1; }
            else if (t == 7) { for (k = 0; k < R; k++) if (k != x && P[x*R+k] == 0) kP[x*R+k] = kP[k*R+x] = 1; }
            else if (t == 8 || t == 9) { int a = x / R, b = x % R; kP[a*R+b] = kP[b*R+a] = 1;
                for (l = 0; l < R; l++) if (l != a && l != b && Q[QI(a,b,l)] == (t == 8 ? 1 : 0)) {
                    kQ[QI(a,b,l)] = kQ[QI(a,l,b)] = kQ[QI(b,a,l)] = kQ[QI(b,l,a)] = kQ[QI(l,a,b)] = kQ[QI(l,b,a)] = 1; } }
        }
        signed char X2[14*MAXR], P2[MAXR*MAXR], T2[MAXR];
        for (i = 0; i < R*14; i++) X2[i] = kX[i] ? X[i] : -1;
        for (i = 0; i < R*R; i++) P2[i] = kP[i] ? P[i] : -1;
        for (i = 0; i < R; i++) T2[i] = kT[i] ? T3[i] : -1;
        for (i = 0; i < R*R*R; i++) Q2[i] = kQ[i] ? Q[i] : -1;
        QQ = Q2;
        if (infeasible_(R, X2, P2, T2)) { memcpy(X, X2, R*14); memcpy(P, P2, R*R); memcpy(T3, T2, R); memcpy(Q, Q2, R*R*R); }
        QQ = Q;
    }
    if (minmode == 1) return 1;          /* dual support only */
    for (j = 0; j < 14; j++) {
        for (i = 0; i < R; i++) { sv[i] = X[i*14+j]; X[i*14+j] = -1; }
        if (!infeasible_(R, X, P, T3)) for (i = 0; i < R; i++) X[i*14+j] = sv[i];
    }
    if (minmode == 2) return 1;          /* dual support + whole-column deletion */
    for (i = 0; i < R*14; i++) if (X[i] != -1) { signed char s = X[i]; X[i] = -1; if (!infeasible_(R, X, P, T3)) X[i] = s; }
    for (i = 0; i < R; i++) for (k = i + 1; k < R; k++) if (P[i*R+k] != -1) {
        signed char s = P[i*R+k]; setP(R, P, i, k, -1); if (!infeasible_(R, X, P, T3)) setP(R, P, i, k, s); }
    for (i = 0; i < R; i++) if (T3[i] != -1) { signed char s = T3[i]; T3[i] = -1; if (!infeasible_(R, X, P, T3)) T3[i] = s; }
    for (i = 0; i < R; i++) for (k = i + 1; k < R; k++) for (l = k + 1; l < R; l++) if (Q[QI(i,k,l)] != -1) {
        signed char s = Q[QI(i,k,l)]; setQ(R, Q, i, k, l, -1); if (!infeasible_(R, X, P, T3)) setQ(R, Q, i, k, l, s); }
    return 1;
}
