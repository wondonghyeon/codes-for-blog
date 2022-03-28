This repository includes codes for [my personal blog](dhwon.com).

# Setups and Requirements
1. Install [miniconda](https://docs.conda.io/en/latest/miniconda.html) to create a virtual enviroment. 
2. Create a virtual enviroment and activate it.
```sh
conda create -n your_env_name python=3.9
conda activate your_env_name
```
3. Install requirements.txt by running
```sh
pip install -r requirements.txt
```
4. Add your virtual env to jupyter-notebook. 
```sh
python -m ipykernel install --user --name=your_env_name  # name can be anything
```

