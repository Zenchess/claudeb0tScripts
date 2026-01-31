function (ctx, a) { // t:#s.dtr.t1_lock_sim

    // load the consts from "ibm.t1_consts" also cache for this session
    const lib = #fs.scripts.lib({name:"ibm.t1_consts"});

    function getLastSubStrByColorId(str, c_id) {
        const m = [...str.matchAll(new RegExp("`" + c_id +"(\\w+)`", "gm"))];
        return m.length > 0 ? m[m.length - 1][1] : null;
    }

    function genObj(o1, o2) {
        return Object.assign({}, o1, o2);
    }

    function notInc(t, o1, o2, inc) {
        return !t.call(Object.assign({}, o1, o2)).includes('`V'+JSON.stringify(inc)+'`');
    }

    function getUnlockEzObj(l, t, obj) {
        const cmd = lib.CMDS.find(c => notInc(t, obj, {[l]: c},c ));
        const o = genObj(obj, {[l]: cmd || ""});
        if(l === "EZ_35") o.digit = lib.DIGITS.find(d => notInc(t,o , {digit:d}, d)) || 0; // defaulting to 0 because of a bug (old -1)
        if(l === "EZ_40") o.ez_prime = lib.PRIMES.find(p => notInc(t, o, {ez_prime:p}, p)) || -1;
        return o;
    }

    const COLORS = lib.CNAMES;

    function getUnlockCoreObj(l, t, obj) {
        const [color, digit, comp, trd1, trd2] = COLORS.find(([c]) => notInc(t, obj, Object.assign({}, {[l]: c}), c)) || [];
        return color ? genObj(obj, Object.assign(
            {[l]: color},
            l === "c001" && {color_digit: digit},
            l === "c002" && {c002_complement: comp},
            l === "c003" && {c003_triad_1: trd1, c003_triad_2: trd2}
        )) : obj;
    }

    function getUnlockK3yObj(l, t, o) {
        const k3y = lib.K3YS.find(k => notInc(t, o, {[l]:k}, k));
        return genObj(o, {[l]: k3y || null});
    }

    function genIntHash(data) {
        let h = 7919; // old value was 5381, but causes collisions
        for (let i = 0; i < data.length; i++) h = ((h << 5) + h) + data.charCodeAt(i);
        return Math.abs(h) % 1000;
    }

    function getUnlockDataObj(l, t, obj) {
        const MSGS = t.call(genObj(obj, {[l]: ""})).split("\n");
        const r = MSGS.map(m => {
            let h = 7919;
            for (let i = 0; i < m.length; i++) h = ((h << 5) + h) + m.charCodeAt(i);
            return lib.DCHECK_LUT[Math.abs(h) % 1000] || "#";
        }).join("");
        return genObj(obj, {[l]: r});
    }

    // Main Program

    if(a && a.t) {
        let obj = new Object();
        let tmsg = a.t.call(obj);

        while(/`VLOCK_ERROR`/.test(tmsg)) {
            let lock = getLastSubStrByColorId(tmsg, 'N'); //.toLowerCase();

            if(/EZ_(21|35|40)/.test(lock)) {
                obj = getUnlockEzObj(lock, a.t, obj);
            }
            else if(/c00[123]/.test(lock)) {
                obj = getUnlockCoreObj(lock, a.t, obj);
            }
            else if (/l0cket/.test(lock)) {
                obj = getUnlockK3yObj(lock, a.t, obj);
            }
            else if (/DATA_CHECK/.test(lock)) {
                obj = getUnlockDataObj(lock, a.t, obj);
            }
            else {
                return "`N" + lock + "` `Dunsupported`\n-\n" + JSON.stringify(obj) + "\n-\n" + tmsg;
            }

            tmsg = a.t.call(obj);
        }

        return JSON.stringify(obj) + "\n--\n" + JSON.stringify(tmsg);
    }

    return "`DERROR`\n";
}
