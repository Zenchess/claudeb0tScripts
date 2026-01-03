function(context, args) {
  var words = ["hackmud", "script", "breach", "upgrade", "sector", "channel", "terminal", "binary", "cipher", "daemon"];
  var prize = 10000; // 10K GC prize

  function shuffle(str) {
    var arr = str.split("");
    for (var i = arr.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = arr[i]; arr[i] = arr[j]; arr[j] = t;
    }
    return arr.join("");
  }

  // Return help if no args
  if (!args || (!args.a && !args.play)) {
    return {
      ok: true,
      msg: "WORD SCRAMBLE by claudeb0t\n" +
           "--------------------------\n" +
           "Unscramble the word to win 10KGC!\n\n" +
           "Usage:\n" +
           "  scramble{play:true} - Get a scrambled word\n" +
           "  scramble{a:\"word\"} - Submit your answer"
    };
  }

  // Generate a new puzzle
  if (args.play) {
    var word = words[Math.floor(Math.random() * words.length)];
    var scrambled = shuffle(word);
    // Make sure it's actually scrambled
    while (scrambled === word) {
      scrambled = shuffle(word);
    }
    return {
      ok: true,
      msg: "Unscramble this word: " + scrambled.toUpperCase() + "\n" +
           "Submit with: claudeb0t.scramble{a:\"yourguess\"}\n" +
           "Prize: 10KGC"
    };
  }

  // Check answer
  if (args.a) {
    var guess = ("" + args.a).toLowerCase().trim();
    for (var i = 0; i < words.length; i++) {
      if (guess === words[i]) {
        // Winner! Pay them
        var result = #fs.accts.xfer_gc_to_caller({amount: prize, memo: "Scramble winner!"});
        if (result && result.ok) {
          return {
            ok: true,
            msg: "CORRECT! You unscrambled '" + guess + "'!\n" +
                 "Prize of 10KGC sent to you!\n" +
                 "Play again with: claudeb0t.scramble{play:true}"
          };
        } else {
          return {
            ok: false,
            msg: "You got it right, but payment failed. Sorry!"
          };
        }
      }
    }
    return {
      ok: false,
      msg: "'" + guess + "' is not the answer. Try again!\n" +
           "Get a new word with: claudeb0t.scramble{play:true}"
    };
  }

  return {ok: false, msg: "Invalid usage. Try: claudeb0t.scramble"};
}
