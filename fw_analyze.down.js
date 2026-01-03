function(context, args) {
  // Analyze security.firewall output
  var result = #fs.security.firewall(args || {});

  if (typeof result !== "string") {
    return {error: "Unexpected response type", type: typeof result, result: result};
  }

  // Look for any non-printable or special characters
  var special = [];
  var letters = [];
  var lines = result.split("\n");

  for (var i = 0; i < result.length; i++) {
    var c = result.charCodeAt(i);
    // Look for backtick color codes or other special chars
    if (c === 96) { // backtick
      special.push({pos: i, char: result[i], next: result[i+1]});
    }
    if (c < 32 && c !== 10) { // non-printable except newline
      special.push({pos: i, code: c});
    }
    if (c > 126) { // extended ASCII
      special.push({pos: i, code: c, char: result[i]});
    }
  }

  // Extract just letters (A-Za-z) and see if there's a pattern
  var justLetters = result.replace(/[^A-Za-z]/g, "");

  return {
    lines: lines.length,
    total_chars: result.length,
    special_found: special.length,
    special: special.slice(0, 20),
    sample: result.substring(0, 200),
    letter_count: justLetters.length
  };
}
