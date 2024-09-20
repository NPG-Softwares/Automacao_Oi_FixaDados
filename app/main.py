import os
from tempfile import TemporaryDirectory
from functions import Oi_Process
from Objects.Obj_ApiSpring import LoginError, get_logins


def main():
    current_dir = os.path.dirname(__file__)
    logins = get_logins('OI', 'hml')

    for login in logins:
        print(f'\n|{"="*60}|')
        print(login)
        with TemporaryDirectory(prefix='oi_', dir=current_dir) as oi_path:
            try:
                Oi_Process(login, oi_path)
            except LoginError as e:
                print(e)
                continue


# Main function execution starts here
if __name__ == "__main__":
    main()
