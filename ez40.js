function(context,args){
if(!args||!args.target)return"ez40{target:#s.npc.loc}";
var t=args.target,r={};
var P=[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97];
var R=t.call(r),s,c,d,cmd;
function has(x){return s.indexOf(x)>-1}
s=""+JSON.stringify(R);
if(!has("EZ_40"))return{err:"no EZ_40",r:R};
cmd=null;
for(c=0;c<3;c++){
r.EZ_40=["unlock","open","release"][c];r.ez_prime=2;
R=t.call(r);s=""+JSON.stringify(R);
if(!has("not the correct unlock")){cmd=["unlock","open","release"][c];break}}
if(!cmd)return{err:"no cmd found",r:R};
r.EZ_40=cmd;
for(d=0;d<P.length;d++){
r.ez_prime=P[d];R=t.call(r);s=""+JSON.stringify(R);
if(has("UNLOCKED")||has("breach"))return{ok:true,r:R,cmd:cmd,prime:P[d]}}
return{ok:false,r:R,cmd:cmd,tried:P.length}}
