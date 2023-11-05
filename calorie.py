def calculate(age, height, weight, gender, goal, exercise):
    BMR = 0
    if gender == "Male":
        BMR = 66.47 + (13.75 * weight) + (5.003 * height) - (6.755 * age)
    elif gender == "Female":
        BMR = 655.1 + (9.563 * weight) + (1.850 * height) - (4.676 * age)
    
    if exercise == "Sedentary":
        BMR *= 1.2
    elif exercise == "Lightly active":
        BMR *= 1.375
    elif exercise == "Moderately active":
        BMR *= 1.55
    elif exercise == "Active":
        BMR *= 1.725
    else:
        BMR *= 1.9

    if goal == "Lose weight":
        BMR *= 0.8
    elif goal == "Gain weight":
        BMR *= 1.2

    return BMR
