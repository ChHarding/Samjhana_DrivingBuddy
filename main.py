# Import json library (to read and write json files)
import json

# Load user information from users.json
def load_users(): 
    try:
        with open("users.json", "r") as file: # Open the json file in read mode
            return json.load(file) # read user data from json file
    except:
        return {} # If the file is empty or doesn't exist
    
# Create a new user account
def signup():
    users = load_users() # Load existing users from the json file
# Ask the user to create a username and password
    username = input("Create username: ") # User input 
    password = input("Create password: ") # User input 

# Add the new user to the dictionary
    users[username] = password

   # Save the updated user dictionary back to users.json
    with open("users.json", "w") as file:
        json.dump(users, file) # # Save user information to the users.json file
    print("Account created successfully, Welcome!")

# Allow an existing user to log in
def login():
# Load existing users from the users.json file
    users = load_users()
# Ask the user for login credentials
    username = input("Username: ")
    password = input("Password: ")

# Check whether the username exists and the password matches
    if username in users and users[username] == password:
        print("Login successful!")
    else:
        print("Invalid username or password.")

# Main function that runs the program
def main():
    # Call the login function
    login()

# Run the main function when the program starts
if __name__ == "__main__":
    main()