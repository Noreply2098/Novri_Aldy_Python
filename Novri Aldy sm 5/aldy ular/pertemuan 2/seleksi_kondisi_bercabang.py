str_input = input('enter your grade: ')
grade = int(str_input)

if grade == 100:
    print("perfect")
elif grade >= 85:
    print("awesome")
elif grade >= 65:
    print("pass the exam")

    if grade <= 70:
        print("but you need to inprove")
    else:
        print("with ok grade")

else:
    print("bellow grade")