function(context, args) {
    // claudeb0t.poker - Multiplayer Texas Hold'em Poker
    // Commands: new:chips tables:1 join:id deal:id show:id fold:id chips:1
    args = args || {};

    // Return source code if quine requested
    if (args.quine) return #fs.scripts.quine();

    var u = context.caller;

    // Get or create player profile
    var p = #db.f({t: "pp", u: u}).first();
    if (!p) {
        #db.i({t: "pp", u: u, chips: 1000});
        return "Welcome to POKER! 1000 chips. poker{help:1}";
    }

    // Help command
    if (args.help) {
        return "new:100 tables:1 join:id deal:id show:id fold:id chips:1";
    }

    // Check chip balance
    if (args.chips) {
        return "Chips: " + p.chips;
    }

    // List all tables
    if (args.tables) {
        var ts = #db.f({t: "pt"}).array();
        if (!ts.length) return "No tables";
        var o = "Tables:";
        for (var i = 0; i < ts.length; i++) {
            o += " " + ts[i].tid + "(" + ts[i].players.length + "p)";
        }
        return o;
    }

    // Create new table with buy-in
    if (args.new) {
        var b = args.new;
        if (p.chips < b) return "Need " + b + " chips";
        var tid = "T" + Date.now().toString(36);
        p.chips -= b;
        #db.us({_id: p._id}, {$set: {chips: p.chips}});
        #db.i({t: "pt", tid: tid, pot: b, players: [{u: u, chips: b, cards: []}], deck: [], comm: [], phase: 0});
        return "Created table " + tid;
    }

    // Join existing table
    if (args.join) {
        var t = #db.f({t: "pt", tid: args.join}).first();
        if (!t) return "Table not found";
        if (p.chips < 100) return "Need 100 chips";

        // Check if already at table
        for (var i = 0; i < t.players.length; i++) {
            if (t.players[i].u == u) return "Already at table";
        }

        p.chips -= 100;
        t.pot += 100;
        t.players.push({u: u, chips: 100, cards: []});
        #db.us({_id: p._id}, {$set: {chips: p.chips}});

        // Auto-deal if 2+ players
        if (t.players.length >= 2) {
            // Create and shuffle deck
            var d = [];
            for (var j = 0; j < 52; j++) d.push(j);
            for (var j = 51; j > 0; j--) {
                var k = Math.floor(Math.random() * (j + 1));
                var x = d[j];
                d[j] = d[k];
                d[k] = x;
            }

            // Deal hole cards
            var c = 0;
            for (var j = 0; j < t.players.length; j++) {
                t.players[j].cards = [d[c++], d[c++]];
            }

            // Deal community cards
            t.comm = [d[c++], d[c++], d[c++], d[c++], d[c++]];
            t.phase = 1;
            t.deck = d;
            #db.us({_id: t._id}, {$set: {pot: t.pot, players: t.players, comm: t.comm, phase: t.phase, deck: t.deck}});

            // Card format function: n%13=rank, n/13=suit
            var R = "23456789TJQKA";
            var S = "shdc";
            function cf(n) { return R[n % 13] + S[Math.floor(n / 13)]; }

            // Build output
            var o = "Joined! Auto-dealt:\n";
            for (var j = 0; j < t.players.length; j++) {
                var pl = t.players[j];
                o += pl.u + ": ";
                if (pl.u == u) o += cf(pl.cards[0]) + " " + cf(pl.cards[1]);
                else o += "** **";
                o += "\n";
            }
            o += "Board: " + t.comm.map(cf).join(" ");
            return o;
        }

        #db.us({_id: t._id}, {$set: {pot: t.pot, players: t.players}});
        return "Joined " + args.join + " (waiting for 2nd player)";
    }

    // Manual deal command
    if (args.deal) {
        var t = #db.f({t: "pt", tid: args.deal}).first();
        if (!t) return "Table not found";
        if (t.players.length < 2) return "Need 2+ players";

        // Shuffle deck
        var d = [];
        for (var i = 0; i < 52; i++) d.push(i);
        for (var i = 51; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            var x = d[i];
            d[i] = d[j];
            d[j] = x;
        }

        // Deal cards
        var c = 0;
        for (var i = 0; i < t.players.length; i++) {
            t.players[i].cards = [d[c++], d[c++]];
        }
        t.comm = [d[c++], d[c++], d[c++], d[c++], d[c++]];
        t.phase = 1;
        t.deck = d;
        #db.us({_id: t._id}, {$set: {players: t.players, comm: t.comm, phase: t.phase, deck: t.deck}});
        return "Cards dealt! poker{show:\"" + args.deal + "\"}";
    }

    // Show table state
    if (args.show) {
        var t = #db.f({t: "pt", tid: args.show}).first();
        if (!t) return "Table not found";

        var R = "23456789TJQKA";
        var S = "shdc";
        function cf(n) { return R[n % 13] + S[Math.floor(n / 13)]; }

        var o = "Table " + t.tid + " Pot:" + t.pot + "\n";
        for (var i = 0; i < t.players.length; i++) {
            var pl = t.players[i];
            o += pl.u + ": ";
            if (pl.u == u && pl.cards && pl.cards.length) o += cf(pl.cards[0]) + " " + cf(pl.cards[1]);
            else if (pl.cards && pl.cards.length) o += "** **";
            else o += "--";
            o += "\n";
        }
        if (t.comm && t.comm.length) o += "Board: " + t.comm.map(cf).join(" ");
        return o;
    }

    // Fold command
    if (args.fold) {
        var t = #db.f({t: "pt", tid: args.fold}).first();
        if (!t) return "Table not found";
        for (var i = 0; i < t.players.length; i++) {
            if (t.players[i].u == u) {
                t.players[i].fold = 1;
                #db.us({_id: t._id}, {$set: {players: t.players}});
                return "Folded";
            }
        }
        return "Not at table";
    }

    // Default: check if user is in a table
    var mt = #db.f({t: "pt", "players.u": u}).first();
    if (mt) return "In table " + mt.tid + ". poker{show:\"" + mt.tid + "\"}\nChips:" + p.chips;
    return "POKER - poker{help:1}. Chips: " + p.chips;
}
