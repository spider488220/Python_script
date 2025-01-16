# Function to validate the mobile number
def validate_mobile(mobile):
    if mobile.isdigit() and len(mobile) == 10:
        return True
    else:
        print("Invalid mobile number. It must be a 10-digit number.")
        return False

# Function to validate the year of birth
def validate_dob(dob):
    if dob.isdigit() and len(dob) == 4 and 1900 < int(dob) <= 2025:
        return True
    else:
        print("Invalid year of birth. It must be a 4-digit year between 1901 and 2025.")
        return False

# Get user input
usr_input_firstname = input("Enter victim's first name: ")
usr_input_surname = input("Enter victim's surname: ")
usr_input_lastname = input("Enter victim's last name: ")
current_year = input("Enter current year: ")

# Validate mobile number input
while True:
    userm = input("Enter a 10-digit mobile number: ")
    if validate_mobile(userm):
        break

# Validate year of birth input
while True:
    dob_year = input("Enter 4-digit DOB year (1901-2025): ")
    if validate_dob(dob_year):
        break

# Get day/month input
daymonths = input("Enter DOB day and month (e.g., 0101): ")

# Prompt for girlfriend's name and year of birth
gf_name = input("Enter girlfriend's name (leave blank if none): ")
gf_dob_year = ""
if gf_name:
    while True:
        gf_dob_year = input("Enter girlfriend's 4-digit DOB year (1901-2025): ")
        if validate_dob(gf_dob_year):
            break

# Prompt for pet name
pet_name = input("Enter pet's name (leave blank if none): ")

# Function to save content to a single file
def save_to_file(content):
    with open("output.txt", "a") as file:  # 'a' mode to append data
        file.write(content + "\n")  # Add a newline after the content

# Function to generate combinations
def generate_combinations(base_name, num_list, userm=None, dob_year=None, daymonths=None):
    base_name_variants = [base_name.capitalize(), base_name.lower()]  # Capitalized and lowercase variants

    for variant in base_name_variants:
        # Add predefined numbers
        for number in num_list:
            save_to_file(f"{variant}{number}")
        
        # Add year of birth and day/month combinations if provided
        if dob_year:
            save_to_file(f"{variant}{dob_year}")
            save_to_file(f"{variant}@{dob_year}")
        if daymonths:
            save_to_file(f"{variant}{daymonths}")
            save_to_file(f"{variant}@{daymonths}")
        
        # Add user input number combinations if provided
        if userm:
            lengths = [4, 6, 8, 10]
            for length in lengths:
                if len(userm) >= length:
                    save_to_file(f"{variant}{userm[:length]}")
                    save_to_file(f"{variant}@{userm[:length]}")

# Main program flow
if __name__ == "__main__":
    # Define the list of predefined numbers
    num_list = [
        "0000", "123", "1234", "12345", "123456",
        "@0000", "@123", "@1234", "@12345", "@123456",
        current_year, f"@{current_year}"
    ]
    
    # Clear the file before starting
    open("output.txt", "w").close()

    # Step 1: Generate combinations with only the first name
    generate_combinations(usr_input_firstname, num_list, userm, dob_year, daymonths)
    
    # Step 2: Generate combinations with first name + surname
    generate_combinations(f"{usr_input_firstname}{usr_input_surname}", num_list, userm, dob_year, daymonths)
    
    # Step 3: Generate combinations with first name + last name
    generate_combinations(f"{usr_input_firstname}{usr_input_lastname}", num_list, userm, dob_year, daymonths)
    
    # Step 4: Generate combinations with first name + surname + last name
    generate_combinations(f"{usr_input_firstname}{usr_input_surname}{usr_input_lastname}", num_list, userm, dob_year, daymonths)
    generate_combinations(f"{usr_input_surname}{usr_input_firstname}", num_list, userm, dob_year, daymonths)
    # Step 5: Generate combinations with girlfriend's name (if provided)
    if gf_name:
        generate_combinations(gf_name, num_list, userm, gf_dob_year, daymonths)
    
    # Step 6: Generate combinations with pet's name (if provided)
    if pet_name:
        generate_combinations(pet_name, num_list)

    print("Processing completed. Check output.txt for results.")
