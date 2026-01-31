function (ctx, a) {

    const WHITE_LIST = /^(ibm|kaj|zenchess|claudeb0t|dunce)$/;

    if(ctx.caller && WHITE_LIST.test(ctx.caller)) {

        return {
            CMDS:["open","unlock","release"],
            DIGITS:[0,1,2,3,4,5,6,7,8,9],
            PRIMES:[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97],

            CNAMES: [
                // [color, color_digit, c002_complement, c003_triad_1, c003_triad_2]
                ["green", 5, "red", "orange", "purple"],
                ["lime", 4, "purple", "red", "blue"],
                ["yellow", 6, "blue", "purple", "cyan"],
                ["orange", 6, "cyan", "blue", "green"],
                ["red", 3, "green", "cyan", "lime"],
                ["purple", 6, "lime", "green", "yellow"],
                ["blue", 4, "yellow", "lime", "orange"],
                ["cyan", 4, "orange", "yellow", "red"]
            ],

            K3YS:["cmppiq","6hh8xw","uphlaw","vc2c7q","tvfkyq","xwz7ja","sa23uw","ellux0",
                "72umy0","i874y3","9p65cu","fr8ibu","eoq6de","xfnkqe","pmvr1q","y111qa"],


            DCHECK_LUT:{
                // integer hashes computed with:
                // function genIntHash(data) {
                //    let h = 7919;
                //    for (let i = 0; i < data.length; i++) h = ((h << 5) + h) + data.charCodeAt(i);
                //    return Math.abs(h) % 1000;
                // }

                // DATA_CHECK_V1
                438:"fran_lee",
                789:"robovac",
                799:"sentience",
                648:"sans_comedy",
                616:"angels",
                500:"minions",
                686:"sisters",
                997:"petra",
                529:"fountain",
                412:"helpdesk",
                211:"bunnybat",
                6:"get_level",
                35:"weathernet",
                479:"eve",
                546:"resource",
                395:"bo",
                448:"heard",
                171:"teach",
                304:"outta_juice",
                547:"poetry",

                // DATA_CHECK_V2
                227:"blazer",
                209:"dead",
                208:"engaged",
                839:"a2231",
                816:"obsessive",
                679:"atlanta",
                993:"skimmerite",
                536:"goodfellow",
                826:"piano",
                809:"idp1p1",
                306:"well",
                897:"nubloopstone",
                308:"sheriff",
                31:"nowhere",
                813:"executives",
                900:"crowsnest",
                371:"thirteen",
                470:"diagalpha",
                494:"bnnyhunter",
                176:"unvarnishedpygmyumbrella",
                851:"making",
                505:"lime",
                80:"110652",
                848:"index",
                382:"mhollister",
                747:"starchart"
            }
        };
    }

    return "`D:::TRUST COMMUNICATION:::` PARSE ERROR "+ ctx.this_script +": script doesn't exist";
}
