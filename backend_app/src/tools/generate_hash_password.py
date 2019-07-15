from werkzeug.security import generate_password_hash

password = input("Enter your password: ")

hashed_password = generate_password_hash(password, method='sha256')

print("Your hash password is  " + hashed_password)