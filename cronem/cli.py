import argparse

def main():
    parser = argparse.ArgumentParser(prog='Cronem', description='Cronometer automation CLI for UofSC dining halls')
    subparsers = parser.add_subparsers(dest='command', required=True)

    subparsers.add_parser('login', help='Set up your Kernel API key and Cronometer login information')
    subparsers.add_parser('add', help='Add or log a custom food to Cronometer')

    args = parser.parse_args()

    if args.command == 'login':
        run_login()
    elif args.command == 'add':
        run_add()

def run_login():
    import getpass
    from pathlib import Path

    env_path = Path.home() / ".cronem" / ".env"
    env_path.parent.mkdir(exist_ok=True)

    api_key = getpass.getpass('Enter your Kernel API key: ')
    username = input('Enter your Cronometer email: ')
    password = input('Enter your Cronometer password: ')

    with open(env_path, 'w') as f:
        f.write(f"KERNEL_API_KEY={api_key}\n")
        f.write(f"CRONOMETER_USERNAME={username}\n")
        f.write(f"CRONOMETER_PASSWORD={password}\n")

    print(f"Credentials saved to {env_path}")

def run_add():
    from . import Kernel

if __name__ == "__main__":
    main()
