# Automating ML Project Initialization with GitHub

## 📌 Overview
Every time I started a new ML project, I wasted 30 minutes creating the same folders, virtual environment, and pushing everything to GitHub. Recently, I’ve been working on ML projects weekly, and I often had to recreate the same folder structure again and again. To save time and focus more on solving business problems, I wrote a project initialization script.  

This README walks you through automating ML project creation and linking it with GitHub.

---

## 🎯 Why Automate ML Project Initialization?

- **Consistency** across all ML projects  
- **Time saved** for actual modeling work  
- **Standardization** in team collaboration  
- **Reduced onboarding friction** when sharing projects  

---

## 🛠️ What This Script Does

This automation script (written in Python) helps you:

- Create a **new GitHub repository**  
- Clone the repository locally  
- Generate a **predefined ML folder structure**  
- Set up a **Python virtual environment**  
- Install dependencies from `requirements.txt`  
- Add an **activation script** for venv  
- Create a `.gitignore` file  
- Create and push a new **Git branch**  

---

## ⚡ Step-by-Step Walkthrough

### 1️⃣ Define Your Ideal Project Structure
We start by defining a reusable folder structure inside the script:

```python
FOLDER_STRUCTURE = [
    ".github/workflows/ci.yml",
    "data/raw/.gitkeep",
    "data/processed/.gitkeep",
    "docs/README.md",
    "models/.gitkeep",
    "notebooks/1.0-eda.ipynb",
    "reports/final_report.md",
    "reports/visualizations/",
    "src/__init__.py",
    "src/data_processing.py",
    "src/train.py",
    "src/predict.py",
    "src/api/main.py",
    "src/api/pydantic_models.py",
    "tests/test_data_processing.py",
    "Dockerfile",
    "docker-compose.yml"
]
```

This ensures every project starts with the same structure.

---

### 2️⃣ Automate GitHub Repo Creation
The script uses the **GitHub API** to create a repo automatically:

```python
def create_github_repo(username, token, repo_name, description):
    url = 'https://api.github.com/user/repos'
    headers = {'Authorization': f'token {token}'}
    data = {'name': repo_name, 'description': description, 'auto_init': True, 'private': False}
    response = requests.post(url, json=data, headers=headers)
```

---

### 3️⃣ Clone Repo & Build Folder Structure

```python
def clone_repo(username, token, repo_name, base_path):
    clone_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
    subprocess.run(['git', 'clone', clone_url, os.path.join(base_path, repo_name)], check=True)
```

The script then creates the full folder structure defined earlier.

---

### 4️⃣ Create Virtual Environment & Install Dependencies

```python
def create_virtual_environment(repo_path, python_exec='python3'):
    venv_path = os.path.join(repo_path, 'venv')
    subprocess.run([python_exec, '-m', 'venv', venv_path], check=True)
```

It also generates a `requirements.txt` with commonly used ML libraries like `numpy`, `pandas`, and `scipy`.

---

### 5️⃣ Add Activation Script

To make environment activation easier, the script generates:

- **Windows** → `activate_venv.bat`  
- **Linux/Mac** → `activate_venv.sh`  

---

### 6️⃣ Create `.gitignore`

A `.gitignore` is automatically created with entries like:

```gitignore
__pycache__/
*.py[cod]
data/
venv/
.env
```

---

### 7️⃣ Push Initial Branch

Finally, the script creates a new branch (default: `task-1`), commits, and pushes it to GitHub.

---

## 📊 Demo

**Before:** Setting up a new project manually (20–30 minutes).  
**After:** Run a single command and the project is ready in under 30 seconds:

```bash
python init_project.py --path /projects --root my-ml-project --desc "ML automation demo"
```

---

## 💡 Lessons Learned

- Keep templates **flexible** but standardized.  
- Automate repetitive tasks to **save mental energy**.  
- Always include `.gitignore` and `requirements.txt` in ML projects.  

---

## 🚀 Try It Yourself

1. Clone this repo  
2. Add your GitHub credentials in a `.env` file:

```env
GITHUB_USERNAME=your-username
GITHUB_TOKEN=your-token
```

3. Run:

```bash
python init_project.py --path /path/to/projects --root my-new-ml-repo --desc --desc "This project is created to automate ml project automation" --python 3.13.1 --branch project-initialization --python python
```
---

## 🙌 Contribute

- ⭐ Star the repo if you find it useful  
- Open an issue or PR to suggest improvements  
- Share how **you automate your ML workflows**  

---

## ✨ Closing Note

> *Automation is the silent force that lets us focus on real ML problems instead of busy work. Start automating today — your future self will thank you.*
