with open("colors.txt", "w") as file:
    file.write("First run:")
    file.write("One\n")
    file.write("Two\n")
    file.write("Three\n")

with open("colors.txt", "a") as file:
    file.write("Second run:")
    file.write("\nThree\n")
    file.write("Two\n")
    file.write("One\n")
    
file = open("colors.txt", "r")
print(file.read())