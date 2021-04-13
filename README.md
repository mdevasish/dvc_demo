create new env

'''bash
conda create -n wineq python=3.7 -y
'''

activate new env

'''bash
conda activate wineq
'''

create requirements.txt file

install the requirements
'''bash
pip install -r requirements.txt
'''

git init

dvc init

dvc add data_given/winequality.csv

git add .

git commit -m "first commit"