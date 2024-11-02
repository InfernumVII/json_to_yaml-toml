# Программа для преобразования JSON в YAML.
# Сначала JSON-строка читается из файла input.json, затем парсится функцией parse_json.
# Функция parse_json определяет, содержит ли строка объект или массив JSON.
# Далее функции parse_object и parse_array обрабатывают объекты и массивы соответственно.
# После получения словаря (или списка) JSON-данных они передаются в функцию json_to_yaml для форматирования в YAML.
# YAML сохраняется в файле output.yaml.

def parse_json(json_str):
    """
    Основная функция парсинга JSON-строки.
    Убирает пробелы и определяет, начинается ли строка с '{' (объект) или '[' (массив).
    Возвращает словарь или список, представляющий JSON-данные.
    """
    json_str = json_str.strip()
    if json_str.startswith('{'):
        return parse_object(json_str[1:])[0]
    elif json_str.startswith('['):
        return parse_array(json_str[1:])[0]
    else:
        raise ValueError("Некорректный JSON: должен начинаться с '{' или '['.")

def skip_whitespace(json_str, i):
    """
    Пропускает пробелы, переходя к следующему символу JSON.
    """
    while i < len(json_str) and json_str[i] in ' \n\t\r':
        i += 1
    return i

def parse_object(json_str):
    """
    Парсит JSON-объект (словарь). Обрабатывает ключи, значения, вложенные объекты и массивы.
    """
    obj = {}
    key = None
    i = 0
    
    while i < len(json_str):
        i = skip_whitespace(json_str, i)
        if i >= len(json_str):
            break
        
        char = json_str[i]
        
        if char == '"':
            # Находим конец строки
            end = json_str.find('"', i + 1)
            if end == -1:
                raise ValueError("Незакрытая строка")
            if key is None:
                # Ключ найден
                key = json_str[i + 1:end]
                i = end + 1
            else:
                # Значение найдено
                obj[key] = json_str[i + 1:end]
                key = None
                i = end + 1

        elif char == ':':
            # Пропускаем двоеточие
            i += 1

        elif char == '{':
            # Обработка вложенного объекта
            nested_obj, length = parse_object(json_str[i + 1:])
            obj[key] = nested_obj
            key = None
            i += length + 1

        elif char == '[':
            # Обработка вложенного массива
            array, length = parse_array(json_str[i + 1:])
            obj[key] = array
            key = None
            i += length + 1

        elif char == '}':
            # Конец объекта
            return obj, i + 1

        elif char == ',':
            key = None
            i += 1

        else:
            if key is not None:
                # Обработка простого значения (числа, логического или null)
                value, length = parse_value(json_str[i:])
                obj[key] = value
                key = None
                i += length
            
    return obj, i

def parse_array(json_str):
    """
    Парсит JSON-массив (список). Обрабатывает объекты, массивы и простые значения.
    """
    array = []
    i = 0

    while i < len(json_str):
        i = skip_whitespace(json_str, i)
        if i >= len(json_str):
            break
            
        char = json_str[i]

        if char == ']':
            # Конец массива
            return array, i + 1

        if char == ',':
            i += 1
            continue

        if char == '{':
            # Обработка вложенного объекта
            obj, length = parse_object(json_str[i + 1:])
            array.append(obj)
            i += length + 2
            continue
            
        # Обработка простого значения
        value, length = parse_value(json_str[i:])
        array.append(value)
        i += length

    return array, i

def parse_value(json_str):
    """
    Парсит простое значение JSON (число, строку, true, false или null).
    """
    i = skip_whitespace(json_str, 0)
    json_str = json_str[i:]
    if not json_str:
        raise ValueError("Пустая строка значения")

    if json_str.startswith('"'):
        # Строка
        end = json_str.find('"', 1)
        if end == -1:
            raise ValueError("Некорректная строка: отсутствует закрывающая кавычка.")
        return json_str[1:end], end + 1
    elif json_str.startswith('{'):
        return parse_object(json_str[1:])
    elif json_str.startswith('['):
        return parse_array(json_str[1:])
    elif json_str.startswith('true'):
        return True, 4
    elif json_str.startswith('false'):
        return False, 5
    elif json_str.startswith('null'):
        return None, 4
    else:
        # Числовое значение
        num_end = 0
        is_float = False
        while num_end < len(json_str) and (json_str[num_end].isdigit() or json_str[num_end] in '.-+'):
            if json_str[num_end] == '.':
                is_float = True
            num_end += 1
        if num_end == 0:
            raise ValueError(f"Некорректное значение: {json_str}")
        if is_float:
            return float(json_str[:num_end]), num_end
        else:
            return int(json_str[:num_end]), num_end

def needs_quotes(value):
    """
    Проверяет, требуется ли обрамление строки в кавычки для YAML.
    """
    return (
        str(value).lower() in ('true', 'false', 'yes', 'no', 'null', 'none') or
        str(value).isnumeric()
    )

def format_string(value):
    """
    Форматирует строки с нужными кавычками для YAML.
    """
    if needs_quotes(value):
        if "'" in str(value):
            value = str(value).replace("'", "''")
        return f"'{value}'"
    return str(value)

def format_multiline(text, indent):
    """
    Форматирует многострочные строки в YAML-синтаксисе.
    """
    if '\n' in text:
        lines = text.split('\n')
        return f" |2\n{' ' * (indent + 2)}" + f"\n{' ' * (indent + 2)}".join(lines)
    return f" {text}"

def json_to_yaml(data, indent=0, indent_size=2, preserve_quotes=True):
    """
    Преобразует JSON-данные в YAML формат.
    """
    yaml_str = ""
    if isinstance(data, dict):
        if not data:
            return " {}\n"
        for key, value in data.items():
            yaml_str += " " * indent + f"{key}:"
            if isinstance(value, (dict, list)):
                if not value:
                    yaml_str += " {}\n" if isinstance(value, dict) else " []\n"
                else:
                    yaml_str += "\n" + json_to_yaml(value, indent + indent_size, indent_size, preserve_quotes)
            else:
                if isinstance(value, str):
                    if '\n' in value:
                        yaml_str += format_multiline(value, indent)
                    elif preserve_quotes and needs_quotes(value):
                        yaml_str += f" {format_string(value)}\n"
                    else:
                        yaml_str += f" {value}\n"
                elif isinstance(value, bool):
                    yaml_str += f" {str(value).lower()}\n"
                elif value is None:
                    yaml_str += " null\n"
                else:
                    yaml_str += f" {value}\n"
    elif isinstance(data, list):
        if not data:
            return " []\n"
        for item in data:
            if isinstance(item, (dict, list)):
                yaml_str += " " * indent + "- " + json_to_yaml(item, indent + indent_size, indent_size, preserve_quotes).lstrip()
            else:
                if isinstance(item, str) and preserve_quotes:
                    item = format_string(item)
                yaml_str += " " * indent + f"- {item}\n"
    else:
        if isinstance(data, str) and preserve_quotes:
            data = format_string(data)
        yaml_str += f"{data}\n"
    return yaml_str

def run():
    """
    Читает JSON из файла и записывает преобразованный YAML в файл.
    """
    with open('input.json', 'r', encoding='utf-8') as f:
        json_text = f.read()

    parsed_data = parse_json(json_text)
    with open('output.yaml', 'w', encoding='utf-8') as f:
        f.write(json_to_yaml(parsed_data))

if __name__ == "__main__":
    run()
