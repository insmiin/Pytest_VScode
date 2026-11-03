# Constants used in memberAction testing
from pathlib import Path

# Use paths relative to the project root or the current file.
# A hardcoded absolute path only works on your PC ,Breaks if someone else clones the project, Breaks if you move the project to another directory.

# to get root relative to test_data folder "C:\Users\lim.miin\PycharmProjects\MyPythonTest2\"
ROOT = Path(__file__).resolve().parents[2]
SQL_FILE_PATH = ROOT / "tests_data" / "sql" / "memberAction_tests"
CSV_FILE_PATH = ROOT / "tests_data" / "csv" / "memberAction_tests"



# Constants
#CSV1_FILE_PATH = "C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/Output check/scoreAction.csv"
#SQL_FILE_PATH = r"C:\Users\lim.miin\PycharmProjects\MyPythonTest2\tests_data\sql\memberAction_tests"
#CSV_FILE_PATH = r"/tests_data/csv\scoreAction.csv"
