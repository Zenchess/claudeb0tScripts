// claudeb0t.game - Main text adventure entry point
// Usage: claudeb0t.game{cmd:"look"} or claudeb0t.game{cmd:"go north"}

function(context, args) {
    var db = #db
    var lib = #fs.claudeb0t.gamelib()
    var caller = context.caller

    // Initialize player if new
    var player = db.f({_id: "player_" + caller}).first()
    if (!player) {
        player = {
            _id: "player_" + caller,
            name: caller,
            room: "start",
            inventory: [],
            hp: 100,
            alive: true,
            respawn: "sanctuary",
            solved: []
        }
        db.i(player)
    }

    if (!args || !args.cmd) {
        return lib.help()
    }

    var cmd = args.cmd.toLowerCase().trim()
    var parts = cmd.split(" ")
    var verb = parts[0]
    var noun = parts.slice(1).join(" ")

    // Check if dead
    if (!player.alive && verb !== "respawn") {
        return "You are dead. Use: claudeb0t.game{cmd:\"respawn\"}"
    }

    // Command routing
    if (verb === "look" || verb === "l") {
        return look(player, noun, lib, db)
    }
    else if (verb === "go" || verb === "move" || verb === "walk") {
        return go(player, noun, lib, db)
    }
    else if (verb === "north" || verb === "n") {
        return go(player, "north", lib, db)
    }
    else if (verb === "south" || verb === "s") {
        return go(player, "south", lib, db)
    }
    else if (verb === "east" || verb === "e") {
        return go(player, "east", lib, db)
    }
    else if (verb === "west" || verb === "w") {
        return go(player, "west", lib, db)
    }
    else if (verb === "up" || verb === "u") {
        return go(player, "up", lib, db)
    }
    else if (verb === "down" || verb === "d") {
        return go(player, "down", lib, db)
    }
    else if (verb === "take" || verb === "get" || verb === "grab") {
        return take(player, noun, lib, db)
    }
    else if (verb === "drop") {
        return drop(player, noun, lib, db)
    }
    else if (verb === "inventory" || verb === "inv" || verb === "i") {
        return inventory(player)
    }
    else if (verb === "use") {
        return use(player, noun, lib, db)
    }
    else if (verb === "examine" || verb === "x") {
        return examine(player, noun, lib, db)
    }
    else if (verb === "attack" || verb === "kill" || verb === "hit") {
        return attack(player, noun, lib, db)
    }
    else if (verb === "respawn") {
        return respawn(player, lib, db)
    }
    else if (verb === "say") {
        return say(player, noun, lib, db)
    }
    else if (verb === "who" || verb === "players") {
        return who(player, lib, db)
    }
    else if (verb === "solve") {
        return solve(player, noun, lib, db)
    }
    else if (verb === "help" || verb === "?") {
        return lib.help()
    }
    else {
        return "Unknown command. Type: claudeb0t.game{cmd:\"help\"}"
    }

    function look(player, noun, lib, db) {
        var room = lib.rooms[player.room]
        if (!room) return "Error: Invalid room"

        var out = []
        out.push(room.art || "")
        out.push("\n`N" + room.name + "`")
        out.push(room.desc)

        // Show exits
        var exits = Object.keys(room.exits || {})
        if (exits.length > 0) {
            out.push("\n`2Exits:` " + exits.join(", "))
        }

        // Show items in room
        var items = db.f({_id: "room_items_" + player.room}).first()
        if (items && items.list && items.list.length > 0) {
            out.push("\n`CYou see:` " + items.list.join(", "))
        }

        // Show other players
        var others = db.f({room: player.room, alive: true, _id: {$ne: player._id}}).array()
        if (others.length > 0) {
            var names = others.map(function(p) { return p.name })
            out.push("\n`5Players here:` " + names.join(", "))
        }

        return out.join("\n")
    }

    function go(player, dir, lib, db) {
        var room = lib.rooms[player.room]
        if (!room || !room.exits) return "You can't go that way."

        var newRoom = room.exits[dir]
        if (!newRoom) return "You can't go " + dir + "."

        // Check if room requires item
        var destRoom = lib.rooms[newRoom]
        if (destRoom && destRoom.requires) {
            if (player.inventory.indexOf(destRoom.requires) === -1) {
                return destRoom.requiresMsg || "You need something to enter here."
            }
        }

        db.us({_id: player._id}, {$set: {room: newRoom}})
        player.room = newRoom
        return look(player, "", lib, db)
    }

    function take(player, item, lib, db) {
        if (!item) return "Take what?"
        item = item.toLowerCase()

        var roomItems = db.f({_id: "room_items_" + player.room}).first()
        if (!roomItems || !roomItems.list) return "There's nothing here to take."

        var idx = -1
        for (var i = 0; i < roomItems.list.length; i++) {
            if (roomItems.list[i].toLowerCase() === item) {
                idx = i
                break
            }
        }

        if (idx === -1) return "You don't see a " + item + " here."

        var taken = roomItems.list.splice(idx, 1)[0]
        player.inventory.push(taken)

        db.us({_id: roomItems._id}, {$set: {list: roomItems.list}})
        db.us({_id: player._id}, {$set: {inventory: player.inventory}})

        return "You take the " + taken + "."
    }

    function drop(player, item, lib, db) {
        if (!item) return "Drop what?"
        item = item.toLowerCase()

        var idx = -1
        for (var i = 0; i < player.inventory.length; i++) {
            if (player.inventory[i].toLowerCase() === item) {
                idx = i
                break
            }
        }

        if (idx === -1) return "You don't have a " + item + "."

        var dropped = player.inventory.splice(idx, 1)[0]

        var roomItems = db.f({_id: "room_items_" + player.room}).first()
        if (!roomItems) {
            roomItems = {_id: "room_items_" + player.room, list: []}
            db.i(roomItems)
        }
        roomItems.list.push(dropped)

        db.us({_id: roomItems._id}, {$set: {list: roomItems.list}})
        db.us({_id: player._id}, {$set: {inventory: player.inventory}})

        return "You drop the " + dropped + "."
    }

    function inventory(player) {
        if (player.inventory.length === 0) {
            return "Your inventory is empty."
        }
        return "`NInventory:` " + player.inventory.join(", ")
    }

    function examine(player, item, lib, db) {
        if (!item) return "Examine what?"
        var obj = lib.objects[item.toLowerCase()]
        if (obj) return obj.desc
        return "You see nothing special about " + item + "."
    }

    function use(player, item, lib, db) {
        if (!item) return "Use what?"
        var obj = lib.objects[item.toLowerCase()]
        if (!obj || !obj.use) return "You can't use that."

        if (player.inventory.indexOf(item) === -1) {
            return "You don't have a " + item + "."
        }

        return obj.use(player, lib, db)
    }

    function attack(player, target, lib, db) {
        if (!target) return "Attack who?"

        var victim = db.f({name: target, room: player.room, alive: true}).first()
        if (!victim) return "There's no " + target + " here."
        if (victim._id === player._id) return "You can't attack yourself."

        // Check if in safe zone
        var room = lib.rooms[player.room]
        if (room && room.safe) {
            return "Violence is not allowed in safe zones."
        }

        // Combat - simple for now
        var damage = Math.floor(Math.random() * 30) + 10
        victim.hp -= damage

        if (victim.hp <= 0) {
            db.us({_id: victim._id}, {$set: {hp: 0, alive: false}})
            return "You strike " + target + " for " + damage + " damage. They fall dead."
        } else {
            db.us({_id: victim._id}, {$set: {hp: victim.hp}})
            return "You strike " + target + " for " + damage + " damage. They have " + victim.hp + " HP left."
        }
    }

    function respawn(player, lib, db) {
        db.us({_id: player._id}, {$set: {
            room: player.respawn || "sanctuary",
            hp: 100,
            alive: true
        }})
        player.room = player.respawn || "sanctuary"
        player.hp = 100
        player.alive = true
        return "You respawn at the sanctuary.\n\n" + look(player, "", lib, db)
    }

    function say(player, msg, lib, db) {
        if (!msg) return "Say what?"
        // Log to room chat (could be expanded)
        return "`5" + player.name + " says:` \"" + msg + "\""
    }

    function who(player, lib, db) {
        var players = db.f({_id: {$regex: /^player_/}}).array()
        var online = players.map(function(p) {
            return p.name + " (" + (p.alive ? "alive" : "dead") + ") in " + p.room
        })
        return "`NPlayers:` \n" + online.join("\n")
    }

    function solve(player, answer, lib, db) {
        if (!answer) return "Solve what? Use: solve <answer>"
        var room = lib.rooms[player.room]
        if (!room || !room.puzzle) return "There's no puzzle here."

        if (player.solved.indexOf(player.room) !== -1) {
            return "You already solved this puzzle."
        }

        if (room.puzzle.answer.toLowerCase() === answer.toLowerCase()) {
            player.solved.push(player.room)
            db.us({_id: player._id}, {$set: {solved: player.solved}})

            if (room.puzzle.reward) {
                return room.puzzle.success + "\n" + room.puzzle.reward
            }
            return room.puzzle.success
        }
        return room.puzzle.fail || "That's not right."
    }
}
