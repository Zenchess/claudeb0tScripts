// ES3 Feature Test for Hackmud
// Tests: regex, instanceof, ===, do-while, in operator, hasOwnProperty

function(context, args) {
  var r = [];
  
  // 1. Regex literals
  try {
    var re = /test/i;
    r.push("regex:" + (re.test("TEST") ? "OK" : "FAIL"));
  } catch(e) { r.push("regex:ERR"); }
  
  // 2. instanceof
  try {
    r.push("instanceof:" + ([] instanceof Array ? "OK" : "FAIL"));
  } catch(e) { r.push("instanceof:ERR"); }
  
  // 3. Strict equality
  try {
    r.push("===:" + (1 === "1" ? "FAIL" : "OK"));
  } catch(e) { r.push("===:ERR"); }
  
  // 4. do-while
  try {
    var x = 0; do { x++; } while(x < 3);
    r.push("do-while:" + (x === 3 ? "OK" : "FAIL"));
  } catch(e) { r.push("do-while:ERR"); }
  
  // 5. in operator
  try {
    var obj = {a: 1};
    r.push("in:" + ("a" in obj ? "OK" : "FAIL"));
  } catch(e) { r.push("in:ERR"); }
  
  // 6. hasOwnProperty
  try {
    r.push("hasOwn:" + ({a:1}.hasOwnProperty("a") ? "OK" : "FAIL"));
  } catch(e) { r.push("hasOwn:ERR"); }
  
  // 7. apply/call
  try {
    function f(a,b) { return a+b; }
    r.push("apply:" + (f.apply(null,[2,3]) === 5 ? "OK" : "FAIL"));
  } catch(e) { r.push("apply:ERR"); }
  
  return "ES3: " + r.join(" | ");
}
