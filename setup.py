import sys, os

def make_service(setup_path):
    with open('tgbot_template.service', 'r') as file:
        template = file.read()
    
    with open('tgbot.service', 'w') as file:
        path_to_exec = os.path.join(setup_path, 'bot.py')
        file.write(template.format(path_to_exec))


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        path = os.path.dirname(os.path.abspath('__file__'))
    else:
        path = sys.argv[1]
    make_service(path)

