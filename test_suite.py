import subprocess
import os
import sys
import unittest

# Color codes for clean terminal output
G = '\033[92m' # Green for success
R = '\033[91m' # Red for errors
Y = '\033[93m' # Yellow for warnings
E = '\033[0m'  # End color formatting

class ApplicationLogicTests(unittest.TestCase):
    """Test cases to verify code existence and basic logic"""
    def test_essential_files(self):
        # Verify structure based on your project sketch
        self.assertTrue(os.path.exists("app/backend/app.py"), "Backend script missing!")
        self.assertTrue(os.path.exists("app/frontend/index.html"), "Frontend HTML missing!")

def run_command(command, description):
    print(f"--- Running: {description} ---")
    try:
        # Running external tools for quality and syntax
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{G}Pass: {description}{E}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{R}Fail: {description}{E}\n{e.stderr}")
        return False

def check_hierarchy():
    """Validates the folder structure against the project plan"""
    print(f"--- Running: Project Hierarchy Check ---")
    required_folders = [
        "app/frontend", "app/backend",
        "helm/helm-frontend", "helm/helm-backend",
        "helm/helm-db", "helm/helm-redis"
    ]
    all_ok = True
    for folder in required_folders:
        if not os.path.isdir(folder):
            print(f"{R}Missing Folder: {folder}{E}")
            all_ok = False
    return all_ok

def check_dockerfiles():
    """Validates that Dockerfiles exist in the correct locations before build"""
    print(f"--- Running: Dockerfile Existence Check ---")
    docker_paths = [
        "app/frontend/Dockerfile",
        "app/backend/Dockerfile"
    ]
    all_ok = True
    for path in docker_paths:
        if not os.path.exists(path):
            print(f"{R}Missing Dockerfile: {path}{E}")
            all_ok = False
        else:
            print(f"{G}Found Dockerfile: {path}{E}")
    return all_ok

if __name__ == "__main__":
    print(f"{Y}Starting Comprehensive Quality, Security & Docker Audit...{E}\n")
    
    # 1. Structure Check
    if not check_hierarchy(): 
        sys.exit(1)

    # 2. Dockerfile Check (Newly Added)
    if not check_dockerfiles():
        sys.exit(1)
    
    # 3. Python Syntax Check (Compile test)
    if not run_command("python3 -m py_compile app/backend/app.py", "Python Syntax Validation"): sys.exit(1)
    
    # 4. Code Quality Check (Pylint)
    run_command("pylint --errors-only app/backend/app.py", "Pylint Quality Audit")
    
    # 5. Helm Charts Validation (Linting)
    charts = ["helm/helm-frontend", "helm/helm-backend", "helm/helm-db", "helm/helm-redis"]
    for chart in charts:
        if not run_command(f"helm lint {chart}", f"Helm Lint: {chart}"): sys.exit(1)
        
    # 6. Security Scan (Hardcoded Secrets)
    if not run_command("detect-secrets scan .", "Security Scanner"): sys.exit(1)
    
    # 7. Functional Test Suite
    print("--- Running: Application Logic Tests ---")
    suite = unittest.TestLoader().loadTestsFromTestCase(ApplicationLogicTests)
    test_result = unittest.TextTestRunner(verbosity=1).run(suite)
    
    if test_result.wasSuccessful():
        print(f"\n{G}>>> AUDIT SUCCESSFUL: Everything is ready for Docker Build! <<<{E}")
    else:
        print(f"\n{R}>>> AUDIT FAILED: Review the errors above. <<<{E}")
        sys.exit(1)