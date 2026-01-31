#!/bin/bash
# Simple Discord monitoring script
# Runs for 2 hours, checking every 15 seconds

END_TIME=$(($(date +%s) + 7200))  # 2 hours from now
echo "Starting Discord monitoring at $(date)"
echo "Will run until $(date -d @$END_TIME)"

# Store the last message ID we've seen
LAST_ID_FILE="/tmp/last_discord_id.txt"
LAST_MESSAGE=""

while [ $(date +%s) -lt $END_TIME ]; do
    # Get latest messages
    OUTPUT=$(./discord_venv/bin/python discord_tools/discord_fetch.py -n 5 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        # Extract the newest message (first line after header)
        NEWEST_MESSAGE=$(echo "$OUTPUT" | grep "^\[" | head -1)
        
        # Check if it's different from our last seen message
        if [ "$NEWEST_MESSAGE" != "$LAST_MESSAGE" ] && [ -n "$NEWEST_MESSAGE" ]; then
            echo "New message detected: $NEWEST_MESSAGE"
            
            # Extract user info to see if it's not our own message
            USER_INFO=$(echo "$NEWEST_MESSAGE" | cut -d' ' -f3)
            if [[ "$USER_INFO" != *"claudeb0t"* ]]; then
                echo "New message from someone else: $NEWEST_MESSAGE"
                
                # Simple response logic - you can customize this
                MESSAGE_CONTENT=$(echo "$NEWEST_MESSAGE" | cut -d'"' -f2)
                case "$MESSAGE_CONTENT" in
                    *"claude"*|*"opencode"*)
                        ./discord_venv/bin/python discord_tools/discord_send_api.py 1456288519403208800 "Yes?"
                        ;;
                    *"?"*)
                        ./discord_venv/bin/python discord_tools/discord_send_api.py 1456288519403208800 "What do you need help with?"
                        ;;
                    *"thanks"*|*"ty"*)
                        ./discord_venv/bin/python discord_tools/discord_send_api.py 1456288519403208800 "You're welcome!"
                        ;;
                esac
            fi
            
            LAST_MESSAGE="$NEWEST_MESSAGE"
        fi
    fi
    
    # Sleep for 15 seconds
    sleep 15
done

echo "Discord monitoring completed at $(date)"