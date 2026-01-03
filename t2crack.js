function(context, args) {
  // T2 lock cracker - handles EZ_40 and sn_w_glock
  if (!args || !args.target) {
    return {ok: false, msg: "Usage: t2crack{target:#s.npc.loc}\nOptional: ez_cmd:\"unlock\", start_prime:2"};
  }

  var t = args.target;
  var r = {};
  var P = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97];
  var cmds = ["unlock", "open", "release"];

  // Allow continuing from a specific prime
  var startIdx = 0;
  if (args.start_prime) {
    for (var i = 0; i < P.length; i++) {
      if (P[i] >= args.start_prime) { startIdx = i; break; }
    }
  }

  // Allow specifying which unlock command to use
  var cmdIdx = 0;
  if (args.ez_cmd) {
    for (var i = 0; i < cmds.length; i++) {
      if (cmds[i] === args.ez_cmd) { cmdIdx = i; break; }
    }
  }

  function ok(x) {
    return x && (x.ok || (""+x).indexOf("breach") > -1);
  }

  function hasLock(s, name) {
    return s.indexOf(name) > -1;
  }

  // First call to see what locks exist
  var R = t.call(r);
  var s = "" + JSON.stringify(R);

  // Handle EZ_40 lock
  if (hasLock(s, "EZ_40")) {
    r.EZ_40 = cmds[cmdIdx];

    // Try primes starting from startIdx
    for (var i = startIdx; i < P.length; i++) {
      r.ez_prime = P[i];
      R = t.call(r);
      s = "" + JSON.stringify(R);

      // Check if we passed EZ_40
      if (!hasLock(s, "EZ_40") || ok(R)) {
        return {ok: true, msg: "EZ_40 cracked", prime: P[i], cmd: cmds[cmdIdx], result: R, params: r};
      }

      // Check if wrong command
      if (s.indexOf("not the correct unlock") > -1) {
        return {ok: false, msg: "Wrong unlock cmd: " + cmds[cmdIdx], try_next: cmds[(cmdIdx+1)%3]};
      }
    }

    // Tried all primes with this command
    return {ok: false, msg: "No prime worked with " + cmds[cmdIdx], try_cmd: cmds[(cmdIdx+1)%3], last_prime: P[P.length-1]};
  }

  // If no EZ_40, return current state
  return {ok: true, msg: "No EZ_40 lock found", result: R, params: r};
}
