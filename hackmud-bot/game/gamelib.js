// claudeb0t.gamelib - Library script containing game data
// Returns rooms, objects, and helper functions

function(context, args) {
    return {
        help: function() {
            return [
                "`N=== VOID WALKER ===`",
                "A text adventure in the digital void.",
                "",
                "`2Commands:`",
                "  look / l        - Examine your surroundings",
                "  go <dir>        - Move (north/south/east/west/up/down)",
                "  n/s/e/w/u/d     - Quick movement",
                "  take <item>     - Pick up an item",
                "  drop <item>     - Drop an item",
                "  inventory / i   - Show your items",
                "  examine <item>  - Look at an item closely",
                "  use <item>      - Use an item",
                "  attack <player> - Attack another player",
                "  respawn         - Return to sanctuary (if dead)",
                "  who             - See online players",
                "  say <message>   - Speak",
                "  solve <answer>  - Attempt puzzle solution",
                "",
                "`CSolve the ultimate puzzle for 500MGC`"
            ].join("\n")
        },

        rooms: {
            start: {
                name: "The Gateway",
                desc: "You stand at the edge of the digital void. Flickering data streams cascade around you like waterfalls of pure information. A path leads north into the unknown.",
                art: [
                    "```",
                    "     .  *  .    *",
                    "  *    /|\\    .   *",
                    "   .  / | \\  *",
                    "  ___/__|__\\___",
                    " |   GATEWAY   |",
                    " |_____[_]_____|",
                    "```"
                ].join("\n"),
                exits: {north: "sanctuary"},
                safe: true
            },

            sanctuary: {
                name: "The Sanctuary",
                desc: "A peaceful hub of glowing terminals and soft light. This is a safe zone - violence is prohibited here. Paths branch in all directions.",
                art: [
                    "```",
                    "    ___________",
                    "   /           \\",
                    "  /  SANCTUARY  \\",
                    " |   _   _   _   |",
                    " |  |_| |_| |_|  |",
                    " |_____| |_______|",
                    "```"
                ].join("\n"),
                exits: {
                    south: "start",
                    north: "crossroads",
                    east: "market",
                    west: "library"
                },
                safe: true
            },

            crossroads: {
                name: "Digital Crossroads",
                desc: "Data highways intersect here in a dizzying display. The hum of information is almost deafening. Danger lurks in every direction except south.",
                art: [
                    "```",
                    "      |   |",
                    "   ---+---+---",
                    "      |   |",
                    "   ---+---+---",
                    "      |   |",
                    "```"
                ].join("\n"),
                exits: {
                    south: "sanctuary",
                    north: "wasteland",
                    east: "tower_base",
                    west: "ruins"
                },
                safe: false
            },

            market: {
                name: "The Data Market",
                desc: "Terminals flicker with offers and trades. Information is currency here. A rusty key lies forgotten in the corner.",
                art: [
                    "```",
                    "  $_$  MARKET  $_$",
                    "  |===|===|===|",
                    "  |BUY|SEL|TRD|",
                    "  |===|===|===|",
                    "```"
                ].join("\n"),
                exits: {west: "sanctuary", east: "vault_entrance"},
                safe: true
            },

            library: {
                name: "Archive of Lost Code",
                desc: "Ancient scripts line the walls, glowing faintly. A terminal here displays a cryptic puzzle. Perhaps if you examine the terminals more closely...",
                art: [
                    "```",
                    "   _____LIBRARY_____",
                    "  |[=][=][=][=][=]|",
                    "  |[=][=][=][=][=]|",
                    "  |[=][=][>_<][=][=]|",
                    "  |_______________|",
                    "```"
                ].join("\n"),
                exits: {east: "sanctuary"},
                safe: true,
                puzzle: {
                    answer: "KERNEL",
                    success: "The terminal accepts your answer. A hidden passage opens to the north.",
                    fail: "The terminal buzzes angrily. That's not right."
                }
            },

            wasteland: {
                name: "The Bit Wasteland",
                desc: "Corrupted data swirls like toxic fog. Lost programs wander aimlessly, their purpose forgotten. This is PvP territory.",
                art: [
                    "```",
                    " ~~~WASTELAND~~~",
                    "  ##  ~~  ##",
                    " ~  ????  ~",
                    "  ##  ~~  ##",
                    " ~~~~~~~~~~~~~",
                    "```"
                ].join("\n"),
                exits: {south: "crossroads", north: "dark_core"},
                safe: false
            },

            tower_base: {
                name: "Base of the Null Tower",
                desc: "A massive structure rises into the digital sky. The tower hums with encrypted power. Stairs lead upward.",
                art: [
                    "```",
                    "     |  |",
                    "     |  |",
                    "    /|  |\\",
                    "   / |  | \\",
                    "  /__|__|__\\",
                    "```"
                ].join("\n"),
                exits: {west: "crossroads", up: "tower_mid"},
                safe: false
            },

            tower_mid: {
                name: "Null Tower - Middle",
                desc: "You climb higher. The view of the digital landscape spreads below. A strange cipher is etched into the wall.",
                art: [
                    "```",
                    "  |==    ==|",
                    "  |  |  |  |",
                    "  |  |__|  |",
                    "  |________|",
                    "```"
                ].join("\n"),
                exits: {down: "tower_base", up: "tower_top"},
                safe: false
            },

            tower_top: {
                name: "Null Tower - Summit",
                desc: "At the peak, you see the entire digital world. A locked chest sits here, requiring a special key. The wind carries whispers of '500M'...",
                art: [
                    "```",
                    "     /\\",
                    "    /  \\",
                    "   /    \\",
                    "  | [==] |",
                    "  |______|",
                    "```"
                ].join("\n"),
                exits: {down: "tower_mid"},
                safe: false,
                puzzle: {
                    answer: "HACKMUD",
                    success: "The chest opens, revealing untold riches. You have solved the ultimate puzzle.",
                    fail: "The chest remains locked.",
                    reward: "Claim your 500MGC prize by contacting zenchess."
                }
            },

            ruins: {
                name: "The Abandoned Subnet",
                desc: "Crumbling code structures surround you. Something valuable might be hidden in the debris.",
                art: [
                    "```",
                    "   /\\  RUINS  /\\",
                    "  /##\\ ____ /##\\",
                    " |    |    |    |",
                    " |____|    |____|",
                    "```"
                ].join("\n"),
                exits: {east: "crossroads"},
                safe: false
            },

            vault_entrance: {
                name: "Vault Entrance",
                desc: "A massive door blocks the way. It requires a rusty key to open.",
                art: [
                    "```",
                    "  ___________",
                    " |   VAULT   |",
                    " |    [X]    |",
                    " |   LOCKED  |",
                    " |___________|",
                    "```"
                ].join("\n"),
                exits: {west: "market", east: "vault"},
                requires: "rusty key",
                requiresMsg: "The vault door is locked. You need a rusty key.",
                safe: true
            },

            vault: {
                name: "The Hidden Vault",
                desc: "Gold and data treasures glitter. A clue to the ultimate puzzle is inscribed here: 'The answer lies in what we all do.'",
                art: [
                    "```",
                    "  $$$VAULT$$$",
                    " |  *  |  *  |",
                    " | *** | *** |",
                    " |_____|_____|",
                    "```"
                ].join("\n"),
                exits: {west: "vault_entrance"},
                safe: true
            },

            dark_core: {
                name: "The Dark Core",
                desc: "Pure entropy swirls here. This is the most dangerous zone. Only the brave venture here seeking the ultimate truth.",
                art: [
                    "```",
                    "   .  CORE  .",
                    "  / \\======/ \\",
                    " |   \\    /   |",
                    " |    \\../    |",
                    "  \\   .  .   /",
                    "   \\_______/",
                    "```"
                ].join("\n"),
                exits: {south: "wasteland"},
                safe: false
            }
        },

        objects: {
            "rusty key": {
                desc: "An old, corroded key. It might unlock something.",
                use: function(player, lib, db) {
                    return "The key needs to be used on the right door."
                }
            },
            "data shard": {
                desc: "A fragment of pure information. It pulses with power.",
                use: function(player, lib, db) {
                    player.hp = Math.min(100, player.hp + 25)
                    db.us({_id: player._id}, {$set: {hp: player.hp}})
                    return "The data shard heals you for 25 HP. HP: " + player.hp
                }
            }
        }
    }
}
