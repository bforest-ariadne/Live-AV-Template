import sys,os

my_path = os.path.abspath(os.path.dirname(__file__))
toe_file = os.path.join(my_path, "../Live-AV-Template.toe")

toe_env_var = 'STARTUP'

toe_env_val = 'dev'

os.environ[toe_env_var] = toe_env_val
os.startfile(toe_file)
print("starting file {} with env val {}".format(toe_file, toe_env_val))