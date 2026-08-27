import shutil
import subprocess
from subprocess import run as run

swipl_path = shutil.which("swipl") or r"C:\Program Files\swipl\bin\swipl.exe"


def query(goal):
    try:
        result = run([swipl_path, "-q", "-g", goal, "-t", "halt", "family.pl"],
                     capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        return False
    except FileNotFoundError:
        return False
    return  result.returncode == 0
g=input("Enter the goal to be executed in Prolog (e.g., ancestor(kin,jack)): ")   

print(query(g))
