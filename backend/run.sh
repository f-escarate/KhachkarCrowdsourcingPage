source .venv/bin/activate

nohup python3 "main.py" > "log" 2>&1 &
echo $! > "save_pid.txt"