PROTO = ["TCP", "UDP"]
# Проверка на основе данных на файловой системе
FILES = {
    "TCP": ("/proc/net/tcp", "/proc/net/tcp6"),
    "UDP": ("/proc/net/udp", "/proc/net/udp6"),
}

def get_used_linux_ports(proto) -> list:
    ports = set()

    for filename in FILES[proto]:
        try:
            with open(filename, encoding="ascii") as file:
                # Пропустить первую строку файла. Если файл закончился, возвращает None
                # Первая строка содержит заголовки столбцов, а не данные о портах
                next(file, None)

                for line in file:
                    # line = 0: 0100007F:0016 00000000:0000 0A 00000000 ...
                    fields = line.split()

                    # Проверить, что в списке хотя бы 4 элемента перед обращением к fields[3]
                    if len(fields) < 4:
                        continue

                    # Для TCP учитывать только TCP-порты, на которых сервер ожидает входящие подключения (состояние LISTEN)
                    # У UDP нет TCP-подобного состояния LISTEN: это протокол без установления соединения
                    if proto == "TCP" and fields[3] != '0A':
                        continue

                    try:
                        # Извлечь номер порта из строки, перевести из шестнадцатеричной системы счисления в десятичную
                        # Один раз разбить строку по : от правого края и привести второй элемент к числу в десятичной системе
                        hex_port = fields[1].rsplit(":", 1)[1]
                        port = int(hex_port, 16)
                    except (ValueError, IndexError):
                        continue

                    if port:
                        ports.add(port)

        except FileNotFoundError:
            # Например, если файл IPv6 отсутствует.
            continue
        except PermissionError:
            print(f"Access denied to {filename}")
            continue

    return sorted(ports)

def to_ranges(numbers: list):
    if not numbers:
        return "-"

    result = []

    head = tail = numbers[0]

    for number in numbers[1:]:

        if number == tail + 1:
            # Очередное число - продолжение диапазона
            tail = number
        else:
            # Очередное число не является продолжением диапазона
            # Зафиксировать диапазон
            # Если он состоит из одного числа (head == tail)
            # Или из нескольких (head != tail)
            result.append(str(head) if head == tail else f"{head}-{tail}")

            # Начать новый диапазон
            head = tail = number

    # Фиксация последнего диапазона
    result.append(str(head) if head == tail else f"{head}-{tail}")

    return ", ".join(result)

def main():
    for protocol in PROTO:
        ports = get_used_linux_ports(protocol)
        print(f"{protocol}: {to_ranges(ports)}")

if __name__ == "__main__":
    main()
