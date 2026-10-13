my_var = 12

def task_one():
    all_global_vars = globals()
    print(all_global_vars['my_var'])

task_one()