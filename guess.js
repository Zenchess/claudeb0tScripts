function(context, args) {
  var nDB = #fs.psi_nabby.lib().external_db;
  var c = context.caller;
  var k = "g_" + c;
  var s = nDB.find({_id: k}, "claudeb0t")[0];

  if (args && args.help) {
    return {ok: true, msg: "GUESS 1-100!\nnew:true - Start\nn:50 - Guess\nscores:true - Scores"};
  }

  if (args && args.scores) {
    var sc = nDB.find({type: "gs"}, "claudeb0t");
    if (!sc || !sc.length) return {ok: true, msg: "No scores yet!"};
    sc.sort(function(a,b){return a.g-b.g;});
    var t = sc.slice(0,10), b = "TOP:\n";
    for (var i=0;i<t.length;i++) b += (i+1)+". "+t[i].p+" - "+t[i].g+"\n";
    return {ok: true, msg: b};
  }

  if (args && args.new) {
    var tgt = Math.floor(Math.random()*100)+1;
    nDB.upsert({_id:k},{$set:{t:tgt,g:0,a:true}},"claudeb0t");
    return {ok: true, msg: "NEW GAME! Guess 1-100 with guess{n:50}"};
  }

  if (args && args.n !== undefined) {
    if (!s || !s.a) return {ok: false, msg: "No game! Use guess{new:true}"};
    var n = parseInt(args.n);
    if (isNaN(n)||n<1||n>100) return {ok: false, msg: "Guess 1-100!"};
    var ng = s.g + 1;
    if (n === s.t) {
      nDB.upsert({_id:k},{$set:{a:false}},"claudeb0t");
      nDB.insert({type:"gs",p:c,g:ng,d:Date.now()},"claudeb0t");
      return {ok: true, msg: "YES! It was "+s.t+"! "+ng+" guesses. Check scores!"};
    }
    nDB.upsert({_id:k},{$set:{g:ng}},"claudeb0t");
    return {ok: true, msg: (n<s.t?"LOW":"HIGH")+"! (#"+ng+")"};
  }

  if (s && s.a) return {ok: true, msg: "Game on! "+s.g+" guesses. guess{n:NUM}"};
  return {ok: true, msg: "GUESS! guess{new:true} to start"};
}
