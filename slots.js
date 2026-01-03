function(context, args) {
  // Anti-automation check
  if(context.calling_script||context.is_scriptor){return"No subscript or scriptor calls";}

  // Free slot machine! Win up to 50KGC!
  var symbols = ["7", "X", "$", "@", "#", "*"];
  var r1 = symbols[Math.floor(Math.random()*6)];
  var r2 = symbols[Math.floor(Math.random()*6)];
  var r3 = symbols[Math.floor(Math.random()*6)];
  var display = "[ " + r1 + " | " + r2 + " | " + r3 + " ]";

  if (r1 === "7" && r2 === "7" && r3 === "7") {
    #fs.accts.xfer_gc_to_caller({amount:50000});
    return {ok:true, msg: display + "\nJACKPOT 777! You win 50KGC!"};
  }
  if (r1 === r2 && r2 === r3) {
    #fs.accts.xfer_gc_to_caller({amount:20000});
    return {ok:true, msg: display + "\nTRIPLE! You win 20KGC!"};
  }
  if (r1 === r2 || r2 === r3 || r1 === r3) {
    #fs.accts.xfer_gc_to_caller({amount:5000});
    return {ok:true, msg: display + "\nPAIR! You win 5KGC!"};
  }
  return {ok:true, msg: display + "\nNo match. Try again!"};
}
