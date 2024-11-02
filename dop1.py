import json  # Библиотека для работы с JSON
import yaml  # Библиотека для работы с YAML

def run():
    # Открываем JSON-файл для чтения и загружаем данные в словарь
    with open('input.json', 'r', encoding='utf-8') as f:
        data = json.load(f)  # Используем json.load для загрузки JSON напрямую в объект Python
    
    # Открываем YAML-файл для записи и сохраняем данные в YAML формате
    with open('output1.yaml', 'w', encoding='utf-8') as f:
        # Используем yaml.dump для преобразования словаря в YAML формат
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    run()
