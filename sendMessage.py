from main import sendMessage


def main():
    TOKEN = input('Введите токен: ')
    HEADER = {'X-Viber-Auth-Token': TOKEN}
    exit = False
    while not exit:
        to = input('Введите id получателя: ')
        while not exit:
            text = input('Введите сообщение: ')
            if text != '':
                sendMessage(to, text=text, header=HEADER)
            exit = True if input('Выйти? (1 для выхода)') == '1' else False


if __name__ == '__main__':
    main()
