grade = int(input('enter your current grade:'))
prev_grade = int(input('enter your previous grade:'))

if grade >= 90 and prev_grade >= 65:
    print("awesome")
if grade >= 90 and prev_grade < 65:
    print("amazing")
if grade <= 65 and prev_grade >= 90:
    print("bro r u ok?")
elif grade >= 65:
    print("passed the exam")
else:
    print("below the passing grade")

if (grade >= 65 and not prev_grade >= 65) or (not grade >= 65 and prev_grade >= 65):
    print("at least you passed one exam")