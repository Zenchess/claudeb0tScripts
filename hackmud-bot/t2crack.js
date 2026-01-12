// T2 Lock Cracker - Brute forces l0cket with pre-solved lock params
// Usage: claudeb0t.t2crack{loc:"user.script", ez_40:"unlock", ez_prime:71, sn_w_glock:"meaning"}
function(context, args) {
    var loc = args.loc;
    if (!loc) return "Usage: t2crack{loc:\"npc.script\", ez_40:\"unlock\", ez_prime:71, sn_w_glock:\"meaning\"}";

    // T2 l0cket passwords (k3y_v2)
    var L = ["hc3b69","5c7e1r","nfijix","4jitu5","vthf6e","lq09tg","voon2h","nyi5u2","j1aa4n","d9j270","vzdt6m","cy70mo","8izsag","hzqgw6","qvgtnt","ooilt2"];

    // Build base params from solved locks
    var p = {};
    if (args.ez_40) p.ez_40 = args.ez_40;
    if (args.ez_prime) p.ez_prime = args.ez_prime;
    if (args.sn_w_glock) p.sn_w_glock = args.sn_w_glock;
    if (args.DATA_CHECK) p.DATA_CHECK = args.DATA_CHECK;
    if (args.c001) p.c001 = args.c001;
    if (args.color_digit) p.color_digit = args.color_digit;
    if (args.c002) p.c002 = args.c002;
    if (args.c002_complement) p.c002_complement = args.c002_complement;

    // Try each l0cket password
    for (var i = 0; i < L.length; i++) {
        p.l0cket = L[i];
        var r = #fs[loc](p);
        if (r && r.ok) return "CRACKED with l0cket:" + L[i] + " - " + JSON.stringify(r);
        var rs = JSON.stringify(r);
        if (rs.indexOf("l0cket") < 0 && rs.indexOf("LOCK_ERROR") < 0) {
            // l0cket is solved, return the response
            return "l0cket solved with: " + L[i] + " - Result: " + rs;
        }
    }
    return "All l0cket passwords tried. Last result: " + JSON.stringify(r);
}
