import sys, os

def make_service(setup_path):
    with open('tgbot_template.service', 'r') as file:
        template: str = file.read()
    
    with open('tgbot.service', 'w') as file:
        file.write(template.format(setup_path))


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        path = os.path.dirname(os.path.abspath('__file__'))
    else:
        path = sys.argv[1]
    make_service(path)

