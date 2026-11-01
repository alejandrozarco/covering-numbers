// Simulated annealing for control_e2e.py: 7 blocks through point 0 are fixed (a link class), the 8 other blocks avoid 0.
// Cost = uncovered triples + 5*(degree deficit below 7) + 5*(pair-degree deficit below 3). Prints the blocks if the
// degree and pair-degree deficits are 0 and at most MAXU triples stay uncovered.
// usage: sa_ext seed iters T0 MAXU b1 ... b56   (the 7 link blocks, 8 points each, design labels 1..17)
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#define V 18
#define K 9
#define B 15
static unsigned long long s; static inline unsigned long long rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
static inline double urand(){return (rnd()>>11)*(1.0/9007199254740992.0);}
int blk[B][K], inb[B][V], cov[V][V][V], lam[V][V], deg[V];
static long cost; static int unc, def;
static inline int *C(int a,int b,int c){int t; if(a>b){t=a;a=b;b=t;} if(b>c){t=b;b=c;c=t;} if(a>b){t=a;a=b;b=t;} return &cov[a][b][c];}
static inline void addp(int b,int ai,int p,int d){ // add (d=1) or remove (d=-1) point p in slot ai of block b
  for(int a=0;a<K;a++){if(a==ai)continue;int x=blk[b][a];
    for(int c=a+1;c<K;c++){if(c==ai)continue;int *t=C(p,x,blk[b][c]);
      if(d>0){if(*t==0)unc--;(*t)++;}else{(*t)--;if(*t==0)unc++;}}
    int u=p<x?p:x,w=p<x?x:p;
    if(d>0){if(lam[u][w]<3)def--;lam[u][w]++;}else{lam[u][w]--;if(lam[u][w]<3)def++;}}
  if(d>0){if(deg[p]<7)def--;deg[p]++;}else{deg[p]--;if(deg[p]<7)def++;}
}
int main(int argc,char**argv){
  s=atoll(argv[1])*2654435761ULL+88172645463325252ULL; long iters=atol(argv[2]); double T0=atof(argv[3]); int maxu=atoi(argv[4]);
  for(int i=0;i<20;i++)rnd();
  for(int i=0;i<7;i++){blk[i][0]=0;for(int a=0;a<8;a++)blk[i][a+1]=atoi(argv[5+i*8+a]);}
  for(int i=7;i<B;i++){int perm[17];for(int p=0;p<17;p++)perm[p]=p+1;
    for(int p=0;p<17;p++){int q=p+rnd()%(17-p);int t=perm[p];perm[p]=perm[q];perm[q]=t;}
    for(int a=0;a<K;a++)blk[i][a]=perm[a];}
  for(int a=0;a<V;a++)for(int b=a+1;b<V;b++)for(int c=b+1;c<V;c++)unc++;
  for(int p=0;p<V;p++){def+=7;for(int q=p+1;q<V;q++)def+=3;}
  for(int i=0;i<B;i++){int sv[K];for(int a=0;a<K;a++)sv[a]=blk[i][a];
    for(int a=0;a<K;a++)for(int b=a+1;b<K;b++)for(int c=b+1;c<K;c++){int *t=C(sv[a],sv[b],sv[c]);if(*t==0)unc--;(*t)++;}
    for(int a=0;a<K;a++){inb[i][sv[a]]=1;if(deg[sv[a]]<7)def--;deg[sv[a]]++;
      for(int b=a+1;b<K;b++){int u=sv[a]<sv[b]?sv[a]:sv[b],w=sv[a]<sv[b]?sv[b]:sv[a];if(lam[u][w]<3)def--;lam[u][w]++;}}}
  cost=unc+5L*def; double T=T0;
  for(long it=0;it<iters;it++){
    if(def==0&&unc<=maxu&&it>iters/2)break;
    int i=7+rnd()%8,ai=rnd()%K,p=blk[i][ai],q;do{q=1+rnd()%17;}while(inb[i][q]);
    addp(i,ai,p,-1);addp(i,ai,q,1);
    long c2=unc+5L*def,d=c2-cost;
    if(d<=0||urand()<exp(-d/T)){blk[i][ai]=q;inb[i][p]=0;inb[i][q]=1;cost=c2;}
    else{addp(i,ai,q,-1);addp(i,ai,p,1);}
    T=T0*(1.0-(double)it/iters)+0.05;
  }
  if(def||unc>maxu)return 1;
  printf("%d",unc);for(int i=0;i<B;i++)for(int a=0;a<K;a++)printf(" %d",blk[i][a]);printf("\n");return 0;
}
