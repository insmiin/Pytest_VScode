import subprocess

# Path to your JMeter test plan (.jmx file)
jmeter_test_plan = "C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/jm/GB test.jmx"

# Optional: specify output file (JTL format)
jmeter_output_file = "C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/results.jtl"

# JMeter command (adjust path to jmeter if not in PATH)
command = [
    "C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/jm/apache-jmeter-5.6.3/bin/jmeter.bat",                 # or full path e.g., "/opt/apache-jmeter-5.6.2/bin/jmeter"
    "-n",                     # non-GUI mode
    "-t", jmeter_test_plan,   # test plan file
    "-l", jmeter_output_file  # result log file
]

# Run JMeter
try:
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("JMeter output:\n", result.stdout)
except subprocess.CalledProcessError as e:
    print("Error running JMeter:\n", e.stderr)
