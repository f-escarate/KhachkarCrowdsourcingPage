import os
from dotenv import load_dotenv

load_dotenv()
UNITY_PATH = os.getenv("UNITY_PATH")
LOGFILE_PATH = os.getenv("LOGFILE_PATH")
PROJECT_PATH = os.getenv("PROJECT_PATH")
UNITY_USER = os.getenv("UNITY_USER")
UNITY_PASSWORD = os.getenv("UNITY_PASSWORD")


def call_method(method, args):
    command = '{0} -quit -batchmode -username "{1}" -password "{2}" -logFile {3} -projectPath {4} -executeMethod {5} {6}'
    return_code = os.system(command.format(UNITY_PATH, UNITY_USER, UNITY_PASSWORD, LOGFILE_PATH, PROJECT_PATH, method, args))
    print(return_code)

if __name__ == "__main__":
    call_method("CallableMethods.GenerateAsset")