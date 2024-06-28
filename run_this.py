import subprocess
import os

# Define paths to the scripts
app_script = os.path.join('website', 'app.py')
main_script = os.path.join('main', 'main.py')

# Start both scripts
app_process = subprocess.Popen(['python', app_script])
main_process = subprocess.Popen(['python', main_script])

# Wait for both scripts to complete (they won't unless interrupted)
app_process.wait()
main_process.wait()
