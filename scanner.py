from scanner.controllers import Controller
from scanner.arguments import get_arguments

if __name__ == "__main__":
    arguments = get_arguments()
    controller = Controller(
        arguments=arguments
    )
    print("All workers are running!")