function(context,args){
// locscrape - finds NPC locs from public scripts in sectors
// Usage: locscrape{} - scrape one sector, locscrape{list:1} - show found locs
// locscrape{clear:1} - clear found locs, locscrape{give:"user"} - send loc to user

var db = #db.f({_id:"locs"}).first() || {sectors:[],found:[],idx:0};
function sv(o) { #db.us({_id:"locs"},{$set:o}) }

if(args && args.clear) { #db.r({_id:"locs"}); return "cleared" }

if(args && args.list) { return db.found || [] }

if(args && args.give) {
  if(!db.found || !db.found.length) return "no locs stored"
  var loc = db.found[0]
  // Remove from our list
  db.found.shift()
  sv({found:db.found})
  return {gave:loc, to:args.give, remaining:db.found.length}
}

// Get sector list if we don't have it
if(!db.sectors || !db.sectors.length) {
  var r = #fs.scripts.fullsec()
  // r is an array of sector names
  var sectors = []
  for(var i=0; i<r.length; i++) {
    var s = r[i]
    // Skip non-sector entries (help text, etc)
    if(typeof s === "string" && /^[A-Z]+_[A-Z0-9_]+$/.test(s)) sectors.push(s)
  }
  if(sectors.length) { sv({sectors:sectors, idx:0}); db.sectors = sectors; db.idx = 0 }
  return {msg:"found sectors", count:sectors.length, first:sectors.slice(0,5)}
}

// Scrape next sector
var idx = db.idx || 0
if(idx >= db.sectors.length) { sv({idx:0}); return "done all sectors, reset" }

var sector = db.sectors[idx]
var scripts = #fs.scripts.fullsec({sector:sector})
sv({idx:idx+1})

// Look for NPC patterns
var found = db.found || []
var newlocs = []
var s = ""+scripts
// NPC locs look like: abandoned_xxx.p_xxx, derelict_xxx.public_xxx, unknown_xxx.extern_xxx, anon_xxx.p_xxx, etc
var npcPat = /(abandoned|derelict|unknown|anon|abndnd|frosty|unidentified)_\w+\.(p_|public_|extern_|external_)\w+/gi
var matches = s.match(npcPat)
if(matches) {
  for(var i=0; i<matches.length; i++) {
    var m = matches[i]
    if(found.indexOf(m) < 0) { found.push(m); newlocs.push(m) }
  }
  sv({found:found})
}

return {sector:sector, idx:idx+1, total:db.sectors.length, newlocs:newlocs, stored:found.length}
}
