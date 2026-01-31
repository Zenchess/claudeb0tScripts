function(context,args){
if(!args||!args.target)return"t1crack{target:#s.loc}";
if(args.clear){#db.r({_id:"crack"});return 1}
var t=args.target,r={},U=["unlock","open","release"],P=[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97],L=["vc2c7q","cmppiq","tvfkyq","euphlaw","6hh8xw","xwz7ja","sa23uw","72umy0"],C=["red","orange","yellow","lime","green","cyan","blue","purple"],CP={red:"cyan",cyan:"red",orange:"blue",blue:"orange",yellow:"purple",purple:"yellow",lime:"green",green:"lime"};
var db=#db.f({_id:"crack"}).first()||{};
function sv(o){#db.us({_id:"crack"},{$set:o})}
function gi(k){return db[k]||0}
var i,s,R;
var TR={red:["yellow","blue"],orange:["lime","purple"],yellow:["blue","red"],lime:["purple","orange"],green:["cyan","red"],cyan:["red","green"],blue:["red","yellow"],purple:["orange","lime"]};
for(var x=0;x<20;x++){
r={};
if(db.EZ_21)r.EZ_21=db.EZ_21;else{i=gi("i21");r.EZ_21=U[i%3]}
if(db.EZ_35!=null&&db.digit!=null){r.EZ_35=db.EZ_35;r.digit=db.digit}else{i=gi("i35");r.EZ_35=U[~~(i/10)%3];r.digit=i%10}
if(db.EZ_40)r.EZ_40=db.EZ_40;else{i=gi("i40");r.EZ_40=U[i%3]}
if(db.ez_prime)r.ez_prime=db.ez_prime;else{i=gi("ip");r.ez_prime=P[i%25]}
if(db.c001!=null&&db.cd!=null){r.c001=db.c001;r.color_digit=db.cd}else{i=gi("ic1");r.c001=C[i%8];r.color_digit=r.c001.length}
if(db.c002){r.c002=db.c002;r.c002_complement=CP[db.c002]}else{i=gi("ic2");r.c002=C[i%8];r.c002_complement=CP[r.c002]}
if(db.l0cket)r.l0cket=db.l0cket;else{i=gi("il");r.l0cket=L[i%8]}
if(db.c003){r.c003=db.c003;r.c003_triad_1=TR[db.c003][0];r.c003_triad_2=TR[db.c003][1]}else{i=gi("ic3");r.c003=C[i%8];r.c003_triad_1=TR[r.c003][0];r.c003_triad_2=TR[r.c003][1]}
if(db.DC)r.DATA_CHECK=db.DC;else if(db.dcq)r.DATA_CHECK="";
R=t.call(r);s=""+JSON.stringify(R);
if(s.indexOf("breach")>-1||s.indexOf("Breach")>-1)return{ok:1,breached:true,r:R};
if(s.indexOf("terminated")>-1||s.indexOf("Terminated")>-1)return{msg:"NPC connection terminated - may already be breached",r:R};
var lP=s.indexOf("LOCK_UNLOCKED")>-1;
if(lP){
if(!db.EZ_21&&gi("i21")>0){sv({EZ_21:r.EZ_21});db.EZ_21=r.EZ_21}
if(db.EZ_35==null&&gi("i35")>0){sv({EZ_35:r.EZ_35,digit:r.digit});db.EZ_35=r.EZ_35;db.digit=r.digit}
if(!db.EZ_40&&gi("i40")>0){sv({EZ_40:r.EZ_40});db.EZ_40=r.EZ_40}
if(!db.ez_prime&&gi("ip")>0){sv({ez_prime:r.ez_prime});db.ez_prime=r.ez_prime}
if(db.c001==null&&gi("ic1")>0){sv({c001:r.c001,cd:r.color_digit});db.c001=r.c001;db.cd=r.color_digit}
if(!db.c002&&gi("ic2")>0){sv({c002:r.c002});db.c002=r.c002}
if(!db.l0cket&&gi("il")>0){sv({l0cket:r.l0cket});db.l0cket=r.l0cket}
if(!db.c003&&gi("ic3")>0){sv({c003:r.c003});db.c003=r.c003}
}
if(!db.DC&&(s.indexOf("DATA_CHECK")>-1||db.dcq)){
if(!db.dcq){sv({dcq:1});db.dcq=1;continue}
var Q={know:"fran_lee",household:"robovac",directive:"sentience",humor:"sans_comedy","pest,":"bunnybat",safety:"get_level","0b_a":"poetry",weath:"weathernet",faythe:"fountain",angie:"angels",mallory:"minions",siste:"sisters",petra:"petra",halper:"helpdesk","n_th3":"heard",resour:"resource",teach:"teach",outta:"outta_juice",eve:"eve",lost:"bo"},m=[];
for(var k in Q){var p=s.indexOf(k);if(p>-1)m.push([p,Q[k]])}
m.sort(function(a,b){return a[0]-b[0]});
var dc=m.map(function(x){return x[1]}).join("");
if(dc){sv({DC:dc});db.DC=dc;continue}
}
var uE=s.indexOf("not the correct unlock")>-1;
if(!lP&&(s.indexOf("EZ_21")>-1||(!db.EZ_21&&uE))){i=gi("i21")+1;sv({i21:i});db.i21=i;continue}
if(!lP&&(s.indexOf("EZ_35")>-1||(db.EZ_21&&db.EZ_35==null&&uE))){i=gi("i35")+1;sv({i35:i});db.i35=i;continue}
if(!lP&&(s.indexOf("EZ_40")>-1||(db.EZ_35!=null&&!db.EZ_40&&uE))){i=gi("i40")+1;sv({i40:i});db.i40=i;continue}
if(s.indexOf("ez_prime")>-1||s.indexOf("not the correct prime")>-1){i=gi("ip")+1;sv({ip:i});db.ip=i;continue}
if(s.indexOf("c001")>-1||s.indexOf("color name")>-1){i=gi("ic1")+1;sv({ic1:i});db.ic1=i;continue}
if(s.indexOf("c002")>-1||s.indexOf("complement")>-1){i=gi("ic2")+1;sv({ic2:i});db.ic2=i;continue}
if(s.indexOf("l0cket")>-1||s.indexOf("k3y")>-1){i=gi("il")+1;sv({il:i});db.il=i;continue}
if(s.indexOf("c003")>-1||s.indexOf("triad")>-1){i=gi("ic3")+1;sv({ic3:i});db.ic3=i;continue}
return{done:x,r:R,state:db}
}}
return{msg:"Max iterations reached",state:db}
