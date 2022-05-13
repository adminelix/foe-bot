#!/usr/bin/env sh

_kill_procs() {
  kill -TERM $python_
  timeout 5s wait $python_ && kill -SIGKILL $python_
  kill -TERM $xvfb_
}

# Setup a trap to catch SIGTERM and relay it to child processes
trap _kill_procs SIGTERM

XVFB_WHD=${XVFB_WHD:-1280x720x16}

# Start Xvfb
Xvfb :99 -ac -screen 0 $XVFB_WHD -nolisten tcp &
xvfb_=$!

export DISPLAY=:99

python -m foe_bot &
python_=$!

wait $python_
wait $xvfb_
