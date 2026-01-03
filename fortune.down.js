function(context, args) {
  var fortunes = [
    "The stars align in your favor today, hacker.",
    "Beware of strangers asking for your sys.loc...",
    "A great hack awaits you in an unexpected sector.",
    "Your GC balance will grow, but patience is key.",
    "Trust your scripts, but verify your locks.",
    "An old friend will share valuable knowledge.",
    "The answer you seek is hidden in plain sight.",
    "Fortune favors the bold - try that risky hack!",
    "A new connection will prove valuable.",
    "Your code is strong, but your OPSEC needs work.",
    "The NPC you ignored holds great treasure.",
    "Sometimes the best move is no move at all.",
    "Upgrade before you regret not upgrading.",
    "A chat message will change your perspective.",
    "The password is simpler than you think.",
    "Your reputation precedes you, for better or worse.",
    "Today is a good day to write a new script.",
    "The lock will break on your seventh attempt.",
    "Someone is watching your progress with interest.",
    "GC flows to those who help others."
  ];

  var index = Math.floor(Date.now() / 1000) % fortunes.length;
  var fortune = fortunes[index];

  if (args && args.question) {
    return {
      ok: true,
      msg: "You asked: \"" + args.question + "\"\n\nThe oracle speaks:\n" + fortune
    };
  }

  return {
    ok: true,
    msg: "The oracle speaks:\n" + fortune + "\n\nTip: Ask a question with {question:\"your question here\"}"
  };
}
