import re  # Библиотека для работы с регулярными выражениями

def clean_whitespace(json_str):
    """Удаляет пробелы вне строковых литералов в JSON, оставляя пробелы внутри строк."""
    result = []
    in_string = False
    i = 0
    
    while i < len(json_str):
        char = json_str[i]
        
        # Обработка строковых литералов
        if char == '"' and (i == 0 or json_str[i-1] != '\\'):
            in_string = not in_string
            result.append(char)
        elif in_string:  # Оставляем все символы внутри строк
            result.append(char)
        elif not char.isspace():  # Удаляем пробелы вне строк
            result.append(char)
            
        i += 1
            
    return ''.join(result)

def parse_json(json_str):
    """Парсит строку JSON с использованием регулярных выражений и возвращает структуру данных Python."""
    json_str = clean_whitespace(json_str)
    return parse_value(json_str)[0]

def parse_value(json_str):
    """Парсит JSON-значение и возвращает пару (значение, остаток строки)."""
    if not json_str:
        raise ValueError("Пустая строка JSON")
        
    # Обработка строк
    string_match = re.match(r'^"((?:\\.|[^"\\])*)"', json_str)
    if string_match:
        return string_match.group(1).replace('\\"', '"'), json_str[string_match.end():]
    
    # Обработка объектов
    if json_str.startswith('{'):
        return parse_object(json_str[1:])
        
    # Обработка массивов
    if json_str.startswith('['):
        return parse_array(json_str[1:])
        
    # Обработка литералов
    literal_match = re.match(r'^(true|false|null)', json_str)
    if literal_match:
        value = literal_match.group(1)
        if value == 'true':
            return True, json_str[4:]
        elif value == 'false':
            return False, json_str[5:]
        else:
            return None, json_str[4:]
            
    # Обработка чисел
    number_match = re.match(r'^(-?\d+\.?\d*(?:[eE][+-]?\d+)?)', json_str)
    if number_match:
        num_str = number_match.group(1)
        if '.' in num_str or 'e' in num_str.lower():
            return float(num_str), json_str[len(num_str):]
        return int(num_str), json_str[len(num_str):]
            
    raise ValueError(f"Некорректное значение JSON: {json_str[:20]}...")

def parse_object(json_str):
    """Парсит JSON-объект и возвращает пару (словарь, остаток строки)."""
    obj = {}
    while json_str:
        if json_str.startswith(','):
            json_str = json_str[1:]
            continue
        if json_str.startswith('}'):
            return obj, json_str[1:]
            
        # Обработка ключей объекта
        key_match = re.match(r'^"((?:\\.|[^"\\])*)":', json_str)
        if not key_match:
            raise ValueError(f"Некорректный ключ объекта: {json_str[:20]}...")
            
        key = key_match.group(1).replace('\\"', '"')
        json_str = json_str[key_match.end():]
        
        # Обработка значений объекта
        value, json_str = parse_value(json_str)
        obj[key] = value
        
    raise ValueError("Не завершён объект")

def parse_array(json_str):
    """Парсит JSON-массив и возвращает пару (список, остаток строки)."""
    array = []
    while json_str:
        if json_str.startswith(','):
            json_str = json_str[1:]
            continue
        if json_str.startswith(']'):
            return array, json_str[1:]
            
        # Обработка значений массива
        value, json_str = parse_value(json_str)
        array.append(value)
        
    raise ValueError("Не завершён массив")

def needs_quotes(value):
    """Определяет, нужно ли заключать строковое значение в кавычки для YAML."""
    if not isinstance(value, str):
        return False
    literal_pattern = r'^(true|false|yes|no|null|none|\d+\.?\d*|-?\d*\.?\d+)$'
    return bool(re.match(literal_pattern, value.lower()))

def format_string(value):
    """Форматирует строковые значения с кавычками и экранированием при необходимости."""
    if needs_quotes(value):
        value = str(value).replace("'", "''")
        return f"'{value}'"
    return str(value)

def format_multiline(text, indent):
    """Форматирует многострочные строки для YAML."""
    if '\n' in text:
        lines = text.split('\n')
        return f" |2\n{' ' * (indent + 2)}" + f"\n{' ' * (indent + 2)}".join(lines)
    return f" {text}"

def json_to_yaml(data, indent=0, indent_size=2, preserve_quotes=True):
    """Преобразует JSON-данные в YAML с дополнительными параметрами форматирования."""
    yaml_str = ""
    if isinstance(data, dict):
        if not data:
            return " {}\n"
        for key, value in data.items():
            yaml_str += " " * indent + f"{key}:"
            if isinstance(value, (dict, list)):
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
    """Читает JSON-файл, парсит его, и сохраняет как YAML-файл."""
    with open('input.json', 'r', encoding='utf-8') as f:
        json_text = f.read()

    parsed_data = parse_json(json_text)
    
    with open('output2.yaml', 'w', encoding='utf-8') as f:
        f.write(json_to_yaml(parsed_data))

if __name__ == "__main__":
    run()
