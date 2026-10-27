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

def ask_yes_no(prompt) -> bool:
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please answer 'y' or 'n'.")


def ask_int(prompt, min_value=None, max_value=None) -> int:
    while True:
        answer = input(prompt).strip()
        try:
            value = int(answer)
        except ValueError:
            print("Please enter a whole number.")
            continue

        if min_value is not None and value < min_value:
            print(f"Please enter a number of at least {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Please enter a number of at most {max_value}.")
            continue

        return value


def main():
    used_tcp = get_used_linux_ports("TCP")

    print(f"Ports in use (TCP): {to_ranges(used_tcp)}")

    # Сначала уточнить, нужно ли подбирать свободные порты или только показать занятые
    select_free = ask_yes_no("Select free TCP ports? (y/n): ")

    if not select_free:
        return

    start = ask_int("Enter the start of the TCP port range: ", min_value=1, max_value=65535)
    while True:
        end = ask_int("Enter the end of the TCP port range: ", min_value=1, max_value=65535)
        if end >= start:
            break
        print("The end of the range must be greater than or equal to the start.")

    count = ask_int("How many free ports do you need? ", min_value=1)

    used = set(used_tcp)
    free_ports = [port for port in range(start, end + 1) if port not in used]

    if len(free_ports) >= count:
        print(f"Free TCP ports in {start}-{end}: {to_ranges(free_ports[:count])}")
    else:
        print(
            f"Not enough free TCP ports in {start}-{end}: "
            f"requested {count}, found {len(free_ports)}."
        )
        if free_ports:
            print(f"Free TCP ports in {start}-{end}: {to_ranges(free_ports)}")

if __name__ == "__main__":
    main()
