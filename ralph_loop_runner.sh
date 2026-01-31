#!/bin/bash
# Ralph Loop Runner - Start and manage the opencode Ralph Loop

RALPH_LOOP_SCRIPT="/home/jacob/hackmud/ralph_loop.py"
PID_FILE="/tmp/ralph_loop.pid"
LOG_FILE="/home/jacob/hackmud/ralph_loop_output.log"

case "$1" in
    start)
        echo "Starting Ralph Loop..."
        if [ -f "$PID_FILE" ]; then
            echo "Ralph Loop is already running (PID: $(cat $PID_FILE))"
            exit 1
        fi
        
        # Start the Ralph Loop in background
        nohup python3 "$RALPH_LOOP_SCRIPT" >> "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "Ralph Loop started (PID: $(cat $PID_FILE))"
        echo "Log file: $LOG_FILE"
        ;;
    
    stop)
        echo "Stopping Ralph Loop..."
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            kill $PID 2>/dev/null
            rm -f "$PID_FILE"
            echo "Ralph Loop stopped"
        else
            echo "Ralph Loop is not running"
        fi
        ;;
    
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat $PID_FILE)
            if ps -p $PID > /dev/null 2>&1; then
                echo "Ralph Loop is running (PID: $PID)"
                echo "Recent log output:"
                tail -20 "$LOG_FILE"
            else
                echo "Ralph Loop PID file exists but process is not running"
                rm -f "$PID_FILE"
            fi
        else
            echo "Ralph Loop is not running"
        fi
        ;;
    
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    
    logs)
        echo "Ralph Loop logs:"
        tail -50 "$LOG_FILE"
        ;;
    
    *)
        echo "Usage: $0 {start|stop|status|restart|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the Ralph Loop in background"
        echo "  stop    - Stop the running Ralph Loop"
        echo "  status  - Check if Ralph Loop is running"
        echo "  restart - Restart the Ralph Loop"
        echo "  logs    - Show recent log output"
        exit 1
        ;;
esac