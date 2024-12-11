This repository includes codes for [my personal blog](https://www.dhwon.com).

**Please note that I'm using an MacOS with an M2 chip and haven't tested on any other enviroments. I'm not doing anything fancy so the code should run on other systems too, but I can't guarantee.**

# Enviroment setup
1. Install [miniconda](https://docs.conda.io/en/latest/miniconda.html).
2. Create a virtual enviroment and activate it. I'll use Python 3.11
```sh
conda create -n your_env_name python=3.10
conda activate your_env_name
```
3. Install the requirements by running
```sh
chmod +x install_pip_requirements.sh
./install_pip_requirements.sh
```
4. Add your virtual env to ipykernel so we can use the enviroment on jupyter notebook.
```sh
python -m ipykernel install --user --name=your_env_name  # name can be anything
5. Modify your PYTHONPATH.
I just put `export "PYTHONPATH=$PYTHONPATH:/Users/dhwon/codes-for-blog/"` in my `~/.bash_profile`.
If you're using vscode, it's convenient to update the `.env`.
```

# Precommit Hook
* Run `pre-commit install`
