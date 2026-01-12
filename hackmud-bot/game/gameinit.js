// claudeb0t.gameinit - Initialize game world (run once)
// Places items in rooms

function(context, args) {
    var db = #db

    // Clear old items
    db.r({_id: {$regex: /^room_items_/}})

    // Place items in rooms
    var items = {
        "room_items_market": {list: ["rusty key"]},
        "room_items_ruins": {list: ["data shard"]},
        "room_items_wasteland": {list: ["data shard"]}
    }

    for (var key in items) {
        db.i({_id: key, list: items[key].list})
    }

    return "Game world initialized. Items placed in rooms."
}
