import subprocess

# List of packages to check
packages = [
    "opencv-python",
    "pyzbar",
    "pyodbc",
    "pandas",
    "streamlit",
    "streamlit-webrtc",
    "numpy",
    "av"
]

print("Checking package versions...\n")

for package in packages:
    try:
        # Run pip show command to get details
        result = subprocess.run(
            ["pip", "show", package],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if line.startswith("Version:"):
                    print(f"{package}: {line.split(' ')[1]}")
        else:
            print(f"{package}: Not installed")
    except Exception as e:
        print(f"Error checking {package}: {e}")
