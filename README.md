# FoE-Bot

## Quickstart

```
# Install pipx if pipenv and cookiecutter are not installed
python3 -m pip install pipx
python3 -m pipx ensurepath

# Install pipenv using pipx
pipx install pipenv

# Use cookiecutter to create project from this template
pipx run cookiecutter gh:sourcery-ai/python-best-practices-cookiecutter

# Enter project directory
cd <repo_name>

# Initialise git repo
git init

# Install dependencies
pipenv install --dev

# Setup pre-commit and pre-push hooks
pipenv run pre-commit install -t pre-commit
pipenv run pre-commit install -t pre-push
```

## signing

- open the city with browser debugger
- find the url of the java script source of the game, `https://foede.innogamescdn.com//cache/ForgeHX-5ac04db0.js` for instance and download that script
- search for `Signature` or better `encode(this._hash+` in the file and you will find a method like 
    ```
  return Ba.substr(SR.encode(this._hash + "ecapLtRKTM1PwXQKiEzaDQDvqdU0y/W7PRZ6yVUX2lc0yEMmPSBOSWpsPRu82oHDQCGt6QWKkuA8jII3lp0A+Q==" + a), 1, 10)
    ```
- the signature are the characters 1-10 of the md5 hash of `playerId` + `RrTNMxkHHQFE2otQVSTZMXcq2gy2zpY5hVG/YyIuDqwV8ZYbYrPnUjEK9R8mqNf2AyY7Zjt5KaRR/BsG2IUxmQ==` + `request body`

