import os
import argparse
import requests
import subprocess
import platform
import logging
from dotenv import load_dotenv
import sys

# === Configure Logging ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# === Load .env Credentials ===
load_dotenv()
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

FOLDER_STRUCTURE = [
    ".github/workflows/ci.yml",             # CI/CD pipeline
    "data/raw/.gitkeep",                    # Raw data placeholder
    "data/processed/.gitkeep",              # Processed data placeholder
    "docs/README.md",                       # Project documentation
    "models/.gitkeep",                      # Trained models storage
    "notebooks/1.0-eda.ipynb",              # EDA and experimentation
    "reports/final_report.md",              # Project analysis/report
    "reports/visualizations/",              # Plots and charts
    "src/__init__.py",                      # Package initializer
    "src/data_processing.py",               # Tokenization, labeling
    "src/train.py",                         # Fine-tuning models
    "src/predict.py",                       # Inference logic
    "src/api/main.py",                      # FastAPI app
    "src/api/pydantic_models.py",           # Pydantic request/response models
    "tests/test_data_processing.py",        # Unit tests
    "Dockerfile",                           # Image config
    "docker-compose.yml"                # Services config
]
# FOLDER_STRUCTURE = [
#     "data/raw/.gitkeep",                # Raw data placeholder
#     "data/processed/.gitkeep",          # Processed data placeholder"
#     "configs/.gitkeep",                 # YAML config files
#     "src/ingestion/",                   # Data loaders and validators       
#     "src/preprocessing/",               # Feature engineering modules
#     "src/modeling/",                    # ML training and evaluation
#     "src/explainability/",              # SHAP and interpretation tools
#     "src/monitoring/",                  # Prefect flows, logging
#     "notebooks/.gitkeep",               # EDA and prototyping
#     "reports/.gitkeep",                 # Model performance summaries
#     "dvc.yaml"                          # DVC pipeline config
# ]


# === STEP 1: Create GitHub Repo ===
def create_github_repo(username, token, repo_name, description):
    logger.info(f"Starting creation of GitHub repository '{repo_name}'")
    url = 'https://api.github.com/user/repos'
    headers = {'Authorization': f'token {token}'}
    data = {
        'name': repo_name,
        'description': description,
        'auto_init': True,
        'private': False
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            logger.info(f"Successfully created repository '{repo_name}' on GitHub")
        elif response.status_code == 422:
            logger.warning(f"Repository '{repo_name}' already exists on GitHub")
        else:
            logger.error(f"GitHub API error: {response.json()}")
            raise Exception(f"GitHub API error: {response.json()}")
    except Exception as e:
        logger.error(f"Failed to create repository: {str(e)}")
        raise

# === STEP 2: Clone the Repo ===
def clone_repo(username, token, repo_name, base_path):
    logger.info(f"Cloning repository '{repo_name}' to {base_path}")
    clone_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
    full_path = os.path.join(base_path, repo_name)
    try:
        subprocess.run(['git', 'clone', clone_url, full_path], check=True)
        logger.info(f"Successfully cloned repository to: {full_path}")
        return full_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone repository: {str(e)}")
        raise

# === STEP 3: Create Folder Structure ===
def create_folder_structure(root_path, structure):
    logger.info(f"Creating folder structure in {root_path}")
    for item in structure:
        path = os.path.join(root_path, item)
        if item.endswith('/') or item.endswith('.gitkeep'):
            # Directory or placeholder file (inside empty directory)
            try:
                os.makedirs(path if item.endswith('/') else os.path.dirname(path), exist_ok=True)
                if item.endswith('.gitkeep'):
                    open(path, 'a').close()
                logger.info(f"Created directory or .gitkeep: {path}")
            except OSError as e:
                logger.error(f"Failed to create folder or .gitkeep {path}: {str(e)}")
                raise
        else:
            # Assume it's a file
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                open(path, 'a').close()
                logger.info(f"Created file: {path}")
            except OSError as e:
                logger.error(f"Failed to create file {path}: {str(e)}")
                raise


# === STEP 4: Create Python Virtual Environment ===
def create_virtual_environment(repo_path, python_exec='python3'):
    venv_path = os.path.join(repo_path, 'venv')
    logger.info(f"Creating virtual environment at: {venv_path} using {python_exec}")
    try:
        subprocess.run([python_exec, '-m', 'venv', venv_path], check=True)
        logger.info("Virtual environment created successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create virtual environment: {str(e)}")
        raise

    # Check if pip is available
    system = platform.system()
    if system == 'Windows':
        pip_path = os.path.join(venv_path, 'Scripts', 'pip.exe')
    else:
        pip_path = os.path.join(venv_path, 'bin', 'pip')
    
    if not os.path.exists(pip_path):
        logger.error(f"pip not found at {pip_path}. Ensure pip is installed in the virtual environment.")
        raise FileNotFoundError(f"pip not found at {pip_path}")

    # Create requirements.txt with common libraries
    req_file = os.path.join(repo_path, 'requirements.txt')
    requirements_content = """# Core data analysis and scientific computing
numpy
pandas
scipy

# Financial analysis
# yfinance
# quantstats

# Data visualization
matplotlib
seaborn
# plotly

# Machine learning
# scikit-learn
# 
# Jupyter notebooks
# jupyter

# Testing
pytest
pytest-cov

# Code quality
black
flake8
"""
    try:
        with open(req_file, 'w') as f:
            f.write(requirements_content)
        logger.info(f"Created requirements.txt at {req_file}")
    except OSError as e:
        logger.error(f"Failed to create requirements.txt: {str(e)}")
        raise

    # Install requirements
    logger.info(f"Installing requirements from {req_file}")
    try:
        subprocess.run([pip_path, 'install', '-r', req_file], check=True)
        logger.info("Successfully installed libraries from requirements.txt")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install requirements: {str(e)}")
        raise

# === STEP 5: Create Activation Script ===
def create_activation_script(repo_path):
    logger.info("Creating virtual environment activation script")
    system = platform.system()
    try:
        if system == 'Windows':
            script_path = os.path.join(repo_path, 'activate_venv.bat')
            with open(script_path, 'w') as f:
                f.write(r'venv\Scripts\activate.bat' + '\n')
            logger.info(f"Created activation script: activate_venv.bat")
            logger.info("To activate venv: run 'activate_venv.bat'")
        else:
            script_path = os.path.join(repo_path, 'activate_venv.sh')
            with open(script_path, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write('source venv/bin/activate\n')
            os.chmod(script_path, 0o755)
            logger.info(f"Created activation script: activate_venv.sh")
            logger.info("To activate venv: run 'source activate_venv.sh'")
    except (OSError, PermissionError) as e:
        logger.error(f"Failed to create activation script: {str(e)}")
        raise

# === STEP 6: Create and push branch ===
def create_and_push_branch(repo_path, branch_name='task-1'):
    logger.info(f"Creating and switching to branch '{branch_name}'")
    try:
        subprocess.run(['git', 'checkout', '-b', branch_name], cwd=repo_path, check=True)
        logger.info(f"Switched to new branch '{branch_name}'")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create branch: {str(e)}")
        raise

    # Add placeholder .keep file to empty folders
    logger.info("Adding .keep files to empty folders")
    for root, dirs, files in os.walk(repo_path):
        for d in dirs:
            dir_path = os.path.join(root, d)
            if not os.listdir(dir_path):  # folder is empty
                keep_file = os.path.join(dir_path, '.keep')
                try:
                    open(keep_file, 'w').close()
                    logger.info(f"Added .keep to empty folder: {dir_path}")
                except OSError as e:
                    logger.error(f"Failed to add .keep to {dir_path}: {str(e)}")
                    raise

    logger.info("Staging changes for commit")
    try:
        subprocess.run(['git', 'add', '.'], cwd=repo_path, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to stage changes: {str(e)}")
        raise

    # Check if there is anything to commit
    status_result = subprocess.run(['git', 'status', '--porcelain'], cwd=repo_path, capture_output=True, text=True)
    if not status_result.stdout.strip():
        logger.warning("Nothing to commit. Project may be empty or already committed.")
        return

    logger.info(f"Committing changes for branch '{branch_name}'")
    try:
        subprocess.run(['git', 'commit', '-m', f'Initialize {branch_name} structure'], cwd=repo_path, check=True)
        logger.info("Changes committed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to commit changes: {str(e)}")
        raise

    logger.info(f"Pushing branch '{branch_name}' to origin")
    try:
        subprocess.run(['git', 'push', '-u', 'origin', branch_name], cwd=repo_path, check=True)
        logger.info(f"Successfully pushed branch '{branch_name}' to GitHub")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to push branch: {str(e)}")
        raise

# === STEP 7: Create .gitignore ===
def create_gitignore(repo_path):
    logger.info(f"Creating .gitignore file in {repo_path}")
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

#data
data/

# Virtual environment
venv/

# macOS system files
.DS_Store

# VSCode settings
.vscode/

# Jupyter Notebook checkpoints
.ipynb_checkpoints/

# Environment variables
.env
"""
    path = os.path.join(repo_path, '.gitignore')
    try:
        with open(path, 'w') as f:
            f.write(gitignore_content)
        logger.info(".gitignore file created successfully")
    except OSError as e:
        logger.error(f"Failed to create .gitignore: {str(e)}")
        raise

# === MAIN FUNCTION ===
def main():
    parser = argparse.ArgumentParser(description='Automate GitHub repo + folder setup + venv + branch')
    parser.add_argument('--path', required=True, help='Directory path to create the project in')
    parser.add_argument('--root', required=True, help='GitHub repo name (also becomes root folder)')
    parser.add_argument('--desc', default='', help='GitHub repository description')
    parser.add_argument('--python', default='python3', help='Python executable to use for virtualenv (e.g. python3.10)')
    parser.add_argument('--branch', default='task-1', help='Name of the Git branch to create and push to')

    args = parser.parse_args()

    logger.info("Starting project setup")
    if not GITHUB_USERNAME or not GITHUB_TOKEN:
        logger.error("GitHub credentials not found. Please set GITHUB_USERNAME and GITHUB_TOKEN in a .env file.")
        raise EnvironmentError(
            "GitHub credentials not found. Please set GITHUB_USERNAME and GITHUB_TOKEN in a .env file.")

    try:
        create_github_repo(GITHUB_USERNAME, GITHUB_TOKEN, args.root, args.desc)
    except Exception as e:
        logger.warning(f"Skipping repo creation due to error: {str(e)}")

    local_repo_path = clone_repo(GITHUB_USERNAME, GITHUB_TOKEN, args.root, args.path)
    create_folder_structure(local_repo_path, FOLDER_STRUCTURE)
    create_gitignore(local_repo_path)
    create_virtual_environment(local_repo_path, args.python)
    create_activation_script(local_repo_path)
    create_and_push_branch(local_repo_path, args.branch)
    logger.info("Project setup completed successfully")

if __name__ == '__main__':
    main()