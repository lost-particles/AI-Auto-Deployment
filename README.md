# 🛠️ Autodeploy CLI

Autodeploy CLI is an intelligent DevOps assistant that takes natural language deployment requests and a code repository (GitHub or ZIP), then:

1. Analyzes the application using Gemini (Google's LLM)
2. Suggests a suitable cloud provider
3. Generates Terraform or proprietary deployment config
4. Offers secure credential capture for optional auto-deployment

---

## 🚀 Features

- **Multi-cloud deployment:** AWS, GCP, Azure, Vercel, Railway, Netlify (easily extensible)
- **LLM-powered intelligence:** Understands app type and deploy context
- **Zero DevOps required:** For developers unfamiliar with infra
- **Configurable Deployment:** Terraform (default) or provider-specific
- **Interactive CLI experience**
- **Step-wise deployment logs**

---

## 🧠 Architecture Overview

```
User Input → CLI → Gemini LLM → Repo Analyzer → App Type + Provider Suggestion
             ↓                                 ↘
         Credential Handler             Deployment Config Generator
             ↓                                 ↓
       Auto-deployment Engine ← Terraform / Vercel / Railway / Netlify
```

---

## ⚙️ Setup Instructions

### 1. Clone and enter project

```bash
git clone https://github.com/yourusername/autodeploy-cli.git
cd autodeploy-cli
```

### 2. Create virtual environment

```bash
conda create -n AIAutoDeploy python=3.10 -y
conda activate AIAutoDeploy
pip install -r requirements.txt
```

### 3. Set your Gemini API key

```bash
export GOOGLE_API_KEY="your_gemini_api_key"
```

---

## 🧪 Example Usage

```bash
python cli.py
```

Inputs:

- A description: *"Deploy this Flask app on Railway"*
- A GitHub repo link or path to `.zip`

CLI does the following:

- Clones/extracts repo
- Scans `requirements.txt`, `README.md`, `package.json`, `Dockerfile`
- Uses Gemini to:
  - detect application type (flask/django/node/etc)
  - recommend cloud provider (fallback to AWS)
- Prompts user to confirm or override provider
- Generates deployable configs (in Terraform or native)
- Offers to auto-deploy using:
  - `terraform` for infra clouds
  - `vercel`, `netlify`, `railway` for platform-specific

---

## 🔐 Credentials

During auto-deployment:

- You’re asked for credentials or tokens
- These are securely stored by `credentials.py`
- Only minimum required access is advised

---

## 🧾 Logs and Output

- `deployment_steps.log`: Chronological action log
- `deployment_configs/`: Stores generated config files for reference or manual use

---

## 🧰 Requirements

```
click
requests
google-generativeai
python-terraform
```

Install CLI tools:

```bash
brew install terraform
npm install -g vercel netlify-cli railway
```

---

## 🗃️ Project Structure

```
.
├── cli.py                     # CLI entry point
├── detector.py                # App type & provider inference + config generation
├── credentials.py             # Safe credential management
├── repo_handler.py            # Repo cloning/unzipping + file introspection
├── utils.py                   # Shared utility methods
├── requirements.txt
├── deployment_steps.log       # Deployment trace log
└── deployment_configs/        # Terraform / other configs saved here
```

---

## ⚠️ Challenges & Fixes

| Challenge                                | Solution                                                           |
| ---------------------------------------- | ------------------------------------------------------------------ |
| Gemini returning long response as 1 blob | Used `###==FILE==###` separator and parsed each file with filename |
| Some providers not supporting Terraform  | Auto-switch to native CLI like `vercel`, `railway`, `netlify`      |
| Missing CLI errors                       | Used `shutil.which()` to check availability before deploying       |
| Gemini returned "any" as provider        | Fallback to `aws`, then allow override via user input              |
| Multi-file config generation             | Parsed LLM response and split into files using special tokens      |

---

## ✨ Future Improvements

- Add `--dry-run` flag for safe preview
- Add CLI auto-installer for missing dependencies
- Add support for container-based or serverless detection
- CI/CD GitHub Actions to lint/test/deploy
- Extend LLM context with `.env` and runtime configs

---

## 🤝 Contributing

PRs and issues welcome! Feel free to fork and build new features.

---

## 📚 Sources and Dependencies

| Source/Dependency                                                     | Description                                                             |
| --------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| [Click](https://palletsprojects.com/p/click/)                         | Used for building CLI interfaces                                        |
| [google-generativeai](https://github.com/google/generative-ai-python) | To interact with Gemini (Generative AI model)                           |
| [python-terraform](https://github.com/beelit94/python-terraform)      | Python wrapper to manage Terraform workflows                            |
| [Terraform CLI](https://developer.hashicorp.com/terraform/cli)        | Used to provision infrastructure                                        |
| [Vercel CLI](https://vercel.com/docs/cli)                             | Native CLI for deploying to Vercel                                      |
| [Netlify CLI](https://docs.netlify.com/cli/get-started/)              | Native CLI for deploying to Netlify                                     |
| [Railway CLI](https://docs.railway.app/develop/cli)                   | Native CLI for deploying to Railway                                     |
| [GitHub](https://github.com/)                                         | Used for cloning and analyzing repositories                             |
| [Gemini API](https://makersuite.google.com/app)                       | Core LLM used to understand user intent, app type, and generate configs |

