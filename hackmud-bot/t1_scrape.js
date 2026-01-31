// t1_scrape.js - Scrape abandoned NPC locs from T1 corps
// Usage: t1_scrape{t:#s.archaic.public} or t1_scrape{t:[#s.archaic.public, #s.futuretech.public]}
// Returns: Array of abandoned NPC locs ready for hacking

function(args) {
    args = _CLONE(typeof args == "object" && args || {});
    
    if (!args.t) {
        return "Usage: t1_scrape{t:#s.archaic.public} or t1_scrape{t:[#s.archaic.public, #s.futuretech.public]}";
    }
    
    // Convert single target to array for unified processing
    let targets = Array.isArray(args.t) ? args.t : [args.t];
    let log = [];
    
    for (let target of targets) {
        try {
            // Validate target structure
            if (typeof target !== 'object' || !target.name || !target.call) {
                log.push(`Error: Invalid target format. Expected {name:string, call:function}`);
                continue;
            }
            
            let corp = target.name.replace('.public', '');
            
            // First, call the corp to get password and project
            let init = target.call({});
            
            if (typeof init !== 'string') {
                log.push(`Error: Could not get initial response from ${target.name}`);
                continue;
            }
            
            // Parse password and project dynamically - look for key:value pairs
            let passwordMatch = init.match(/password:\s*(\w+)/i);
            let projectMatch = init.match(/project:\s*(\w+)/i);
            
            if (!passwordMatch || !projectMatch) {
                log.push(`Error: Could not parse password and project from ${target.name} response`);
                continue;
            }
            
            let PASSWORD = passwordMatch[1];
            let PROJECT = projectMatch[1];
            
            // Build dynamic navigation parameters
            let navParams = {
                p: PASSWORD,
                project: PROJECT
            };
            
            // Try different navigation keys that might exist
            let navKeys = ["personnel", "employees", "staff", "roster"];
            let result = null;
            
            for (let navKey of navKeys) {
                try {
                    let testParams = Object.assign({}, navParams, {navigation: navKey});
                    result = target.call(testParams);
                    
                    if (result && typeof result === 'string' && result.length > 10) {
                        break; // Found a working navigation key
                    }
                } catch (e) {
                    // Continue to next navigation key
                    continue;
                }
            }
            
            if (!result) {
                log.push(`Error: Could not access ${corp} personnel data with any navigation key`);
                continue;
            }
            
            // Clean corruption characters: [backtick, color code, corruption char, backtick]
            let cleanText = result.replace(/`[a-zA-Z0-9]`.`/g, '');
            
            // Parse the cleaned response to extract locs
            let locs = [];
            let lines = cleanText.split('\n');
            
            for (let line of lines) {
                // Match loc patterns: unknown_, unidentified_, anonymous_, derelict_, uknown_ etc.
                let locMatch = line.match(/\b(unknown|unidentified|anonymous|derelict|uknown)_[a-z0-9]+\b/g);
                
                if (locMatch) {
                    for (let loc of locMatch) {
                        // Avoid duplicates
                        if (!locs.includes(loc)) {
                            locs.push(loc);
                        }
                    }
                }
            }
            
            // Format the output for easy use
            if (locs.length > 0) {
                log.push(`Found ${locs.length} abandoned NPC locs from ${corp}:\n` + 
                       locs.map((loc, i) => `${i+1}. ${loc}`).join('\n') + 
                       `\nUse with: claudeb0t.t1crack{target:#s.${loc}}`);
            } else {
                log.push(`No abandoned locs found from ${corp}. Try again later - data may have changed.`);
            }
            
        } catch (error) {
            log.push(`Error scraping ${target.name}: ${error.toString()}`);
        }
    }
    
    return log.join('\n\n');
}