# Chat with repo

## Development setup

**linux/osx**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**win**
```bash
python3.exe -m venv .venv
.\.venv\Scripts\activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```


## Configuration
- copy .env.template to .env
- set the following variables in .env
  - `GITHUB_TOKEN`
  - `OPENAI_API_KEY`
  - `UTHORIZED_USERS`
  - `MODEL_NAME`

## Run
**linux/osx**
```bash
streamlit run chat_with_repo/app.py
```

**win**
```bash
streamlit run chat_with_repo\app.py
```