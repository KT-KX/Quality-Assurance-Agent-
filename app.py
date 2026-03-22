# app.py - The code the Agent needs to check

def process_user_name(name):
    """
    Capitalizes the first letter of the name.
    BUG: If the name is an empty string, name[0] will throw an IndexError.
    """
    if name is None:
        return "Guest"
    
    # This line will crash if name == ""
    formatted_name = name[0].upper() + name[1:].lower()
    return formatted_name

if __name__ == "__main__":
    print(process_user_name("uncle")) # Works
    print(process_user_name(""))    # WILL CRASH
    print("halo halo")
