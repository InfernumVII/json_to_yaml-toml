"""
Программа для преобразования данных из формата JSON в формат TOML.

Краткое устройство программы:
1. Функция `format_string` — форматирует строки для TOML, чтобы они корректно отображались с учетом специальных символов и кавычек.
2. Функция `format_value` — форматирует значения разных типов (строки, числа, логические значения и т.д.) в формат TOML.
3. Функция `json_to_toml` — рекурсивно обрабатывает структуру JSON, конвертируя ее в структуру TOML, поддерживая вложенные объекты, массивы и таблицы.
4. Основной блок программы считывает JSON из файла, парсит его и сохраняет результат в формате TOML в выходной файл.

"""

from datetime import datetime
import main as m

def format_string(s):
    """Форматирует строки для TOML, добавляя кавычки или обрамляя тройными кавычками для многострочных данных."""
    if '\n' in s:
        return f'"""\n{s}\n"""'
    elif '"' in s:
        return f"'{s}'"
    else:
        return f'"{s}"'

def format_value(value):
    """Форматирует значение для TOML в зависимости от его типа данных."""
    if isinstance(value, str):
        return format_string(value)
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    elif value is None:
        return ''
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, (list, tuple)):
        # Пустой список
        if not value:
            return '[]'
        # Если список состоит только из простых типов
        if all(isinstance(x, (int, float, str, bool)) for x in value):
            items = [format_value(x) for x in value]
            return f'[{", ".join(items)}]'
        else:
            # Многострочное форматирование для сложных элементов списка
            items = [format_value(x) for x in value]
            return '[\n  ' + ',\n  '.join(items) + '\n]'
    else:
        raise ValueError(f"Unsupported type for TOML: {type(value)}")

def json_to_toml(data, prefix=''):
    """
    Конвертирует структуру JSON в формат TOML.

    Args:
        data (dict): Входные данные JSON.
        prefix (str): Префикс для ключей (используется для вложенных таблиц).
    
    Returns:
        str: Строка TOML-формата.
    """
    result = []
    
    if isinstance(data, dict):
        # Обработка простых пар ключ-значение
        for key, value in data.items():
            if not isinstance(value, (dict, list)):
                if value is not None:  # Пропускаем значения null
                    full_key = f'{prefix}{key}' if prefix else key
                    result.append(f'{full_key} = {format_value(value)}')
        
        # Обработка массивов
        for key, value in data.items():
            if isinstance(value, list):
                full_key = f'{prefix}{key}' if prefix else key
                if value and all(isinstance(x, dict) for x in value):
                    # Массив таблиц
                    for item in value:
                        result.append(f'\n[[{full_key}]]')
                        result.append(json_to_toml(item, prefix=full_key + '.'))
                else:
                    # Обычный массив
                    if value:  # Пропускаем пустые массивы
                        result.append(f'{full_key} = {format_value(value)}')
        
        # Обработка вложенных таблиц
        for key, value in data.items():
            if isinstance(value, dict):
                full_key = f'{prefix}{key}' if prefix else key
                result.append(f'\n[{full_key}]')
                result.append(json_to_toml(value))
                
    return '\n'.join(result)

# Основной блок программы
if __name__ == "__main__":
    with open('input.json', 'r', encoding='utf-8') as f:
        json_text = f.read()

    # Парсинг JSON-данных
    parsed_data = m.parse_json(json_text)
    
    # Запись результата в формат TOML
    with open('output.toml', 'w', encoding='utf-8') as f:
        f.write(json_to_toml(parsed_data))
