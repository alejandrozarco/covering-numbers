// Simulated annealing for (v,k,3) covering with b blocks. Usage: sa v k b seed iters T0
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#define MAXV 32
int v,k,b; int blk[64][MAXV]; int inb[64][MAXV]; unsigned char cov[MAXV][MAXV][MAXV];
static unsigned long long s; static inline unsigned long long rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
static inline double urand(){return (rnd()>>11)*(1.0/9007199254740992.0);}
static inline int C3(int a,int b2,int c){ // sort
  int t; if(a>b2){t=a;a=b2;b2=t;} if(b2>c){t=b2;b2=c;c=t;} if(a>b2){t=a;a=b2;b2=t;} return cov[a][b2][c];}
static inline void add3(int a,int b2,int c,int d){int t; if(a>b2){t=a;a=b2;b2=t;} if(b2>c){t=b2;b2=c;c=t;} if(a>b2){t=a;a=b2;b2=t;} cov[a][b2][c]+=d;}
int main(int argc,char**argv){v=atoi(argv[1]);k=atoi(argv[2]);b=atoi(argv[3]);s=atoll(argv[4])*2654435761ULL+1;long iters=atol(argv[5]);double T0=atof(argv[6]);
 for(int r=0;r<64 && r<atoi(argv[4])%7+3;r++) rnd();
 memset(cov,0,sizeof cov);
 for(int i=0;i<b;i++){int perm[MAXV];for(int p=0;p<v;p++)perm[p]=p;for(int p=0;p<v;p++){int q=p+rnd()%(v-p);int t=perm[p];perm[p]=perm[q];perm[q]=t;}
  memset(inb[i],0,sizeof inb[i]);for(int a=0;a<k;a++){blk[i][a]=perm[a];inb[i][perm[a]]=1;}
  for(int a=0;a<k;a++)for(int c=a+1;c<k;c++)for(int d=c+1;d<k;d++)add3(blk[i][a],blk[i][c],blk[i][d],1);}
 int unc=0;for(int a=0;a<v;a++)for(int c=a+1;c<v;c++)for(int d=c+1;d<v;d++)if(!cov[a][c][d])unc++;
 int best=unc; double T=T0;
 for(long it=0;it<iters;it++){
  if(unc==0)break;
  int i=rnd()%b; int ai=rnd()%k; int p=blk[i][ai]; int q; do{q=rnd()%v;}while(inb[i][q]);
  // delta: removing p loses triples {p,x,y} x,y in blk\p with cov==1; adding q gains {q,x,y} x,y in blk\p with cov==0
  int delta=0;
  for(int a=0;a<k;a++){if(a==ai)continue;for(int c=a+1;c<k;c++){if(c==ai)continue;int x=blk[i][a],y=blk[i][c];
    if(C3(p,x,y)==1)delta++; if(C3(q,x,y)==0)delta--;}}
  if(delta<=0 || urand()<exp(-delta/T)){
    for(int a=0;a<k;a++){if(a==ai)continue;for(int c=a+1;c<k;c++){if(c==ai)continue;int x=blk[i][a],y=blk[i][c];add3(p,x,y,-1);add3(q,x,y,1);}}
    blk[i][ai]=q;inb[i][p]=0;inb[i][q]=1;unc+=delta; if(unc<best){best=unc;}
  }
  T=T0*(1.0-(double)it/iters)+1e-3;
  if((it&((1<<24)-1))==0){fprintf(stderr,"it %ld unc %d best %d T %.3f\n",it,unc,best,T);}
 }
 printf("final unc %d best %d\n",unc,best);
 if(unc<=1){for(int i=0;i<b;i++){for(int a=0;a<k;a++)printf("%d ",blk[i][a]);printf("\n");}}
 return 0;}
