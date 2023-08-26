This repository includes codes for [my personal blog](dhwon.com).

**Please note that I'm using MacOS (with an Intel chip) and haven't tested on any other enviroments. I'm not doing anything fancy so the code should run on other systems too, but I can't guarantee.**

# Enviroment setup
1. Install [miniconda](https://docs.conda.io/en/latest/miniconda.html). 
2. Create a virtual enviroment and activate it.
```sh
conda create -n your_env_name python=3.11
conda activate your_env_name
```
3. Install the requirements by running
```sh
pip install -r requirements.txt
```
4. Add your virtual env to ipykernel so we can use the enviroment on jupyter notebook. 
```sh
python -m ipykernel install --user --name=your_env_name  # name can be anything
```


# TODOs
- [] Set up precommit hook