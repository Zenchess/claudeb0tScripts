// GC transfer script - caller receives GC
// Usage: claudeb0t.gc{amount:42}
function(context, args) {
    var amount = args.amount;
    if (!amount || amount <= 0) {
        return "Usage: claudeb0t.gc{amount:<number>}";
    }

    var result = #fs.accts.xfer_gc_to_caller({amount: amount});
    if (result.ok) {
        return "Sent " + amount + "GC to " + context.caller;
    } else {
        return "Transfer failed: " + JSON.stringify(result);
    }
}
