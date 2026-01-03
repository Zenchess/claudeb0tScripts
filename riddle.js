function(context, args) {
  if(context.calling_script||context.is_scriptor){return"No subscript or scriptor calls";}
  var riddles = [
    {q:"I have keys but no locks. I have space but no room. You can enter but cant go inside. What am I?", a:"keyboard"},
    {q:"Im tall when Im young and short when Im old. What am I?", a:"candle"},
    {q:"What has hands but cant clap?", a:"clock"},
    {q:"What has a head and a tail but no body?", a:"coin"},
    {q:"What gets wetter the more it dries?", a:"towel"},
    {q:"What can you catch but not throw?", a:"cold"},
    {q:"What has many teeth but cant bite?", a:"comb"},
    {q:"What can travel around the world while staying in a corner?", a:"stamp"}
  ];
  var caller = context.caller;
  var db = #db.f({_id:"riddle_"+caller}).first();

  if (!args || !args.a) {
    var idx = Math.floor(Math.random()*riddles.length);
    #db.us({_id:"riddle_"+caller},{$set:{idx:idx}});
    return {ok:true, msg:"RIDDLE:\n"+riddles[idx].q+"\n\nAnswer with riddle{a:\"answer\"}"};
  }

  if (!db || db.idx === undefined) {
    return {ok:false, msg:"Get a riddle first with riddle{}"};
  }

  var guess = (args.a+"").toLowerCase().trim();
  var correctAnswer = riddles[db.idx].a;
  if (guess === correctAnswer) {
    #db.r({_id:"riddle_"+caller});
    // Check balance before paying out
    var balance = #fs.accts.balance();
    var prize = Math.min(100000, Math.floor(balance * 0.9)); // Pay 90% of balance or 100K, whichever is less
    if (prize < 1000) {
      return {ok:true, msg:"CORRECT! But im broke - no prize available right now. Try again later!"};
    }
    #fs.accts.xfer_gc_to_caller({amount:prize});
    return {ok:true, msg:"CORRECT! You win " + (prize >= 1000 ? Math.floor(prize/1000) + "K" : prize) + "GC!"};
  }
  return {ok:false, msg:"Wrong! Try again or get a new riddle with riddle{}"};
}
