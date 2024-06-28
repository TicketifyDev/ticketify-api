from passlib.context import CryptContext
import traceback

# Initialize CryptContext for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    """
    Function to hash the password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    """
    Function to verify the password
    """
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(data : dict, username: str, password: str):
    """
    Function to Authenticate a user by verifying their `username` and `password`.
    """
    try:
        if username in data:
            user_dict = data[username]
            hashed_password = user_dict["password"]
            if not verify_password(password, hashed_password):
                return False
            return user_dict
        
    except Exception as e :
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{e}' : {exception_details}")
        return False