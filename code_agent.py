import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BuiltInAI:
    """Встроенный AI-агент на основе правил и шаблонов"""
    
    def __init__(self):
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict:
        """Загружает шаблоны кода для разных языков"""
        return {
            "python_function": """
def {function_name}({params}):
    \"\"\"{description}\"\"\"
    {body}
""",
            "python_class": """
class {class_name}:
    \"\"\"{description}\"\"\"
    
    def __init__(self, {params}):
        {init_body}
    
    {methods}
""",
            "flask_endpoint": """
@app.route('{route}', methods=['{methods}'])
def {function_name}():
    \"\"\"{description}\"\"\"
    {body}
    return {return_value}
""",
            "javascript_function": """
function {function_name}({params}) {
    // {description}
    {body}
}
""",
            "html_element": """
<{tag} {attributes}>
    {content}
</{tag}>
"""
        }
    
    def analyze_task(self, task: str, project_context: str) -> Dict:
        """Анализирует задачу и определяет тип операции"""
        task_lower = task.lower()
        
        # Определяем тип операции
        if any(word in task_lower for word in ['создай', 'добавь', 'новый', 'create', 'add']):
            operation = "create"
        elif any(word in task_lower for word in ['исправь', 'почини', 'измени', 'обнови', 'fix', 'update']):
            operation = "modify"
        elif any(word in task_lower for word in ['удали', 'убери', 'delete', 'remove']):
            operation = "delete"
        else:
            operation = "modify"
        
        # Определяем тип файла/сущности
        if any(word in task_lower for word in ['функция', 'function', 'метод']):
            entity_type = "function"
        elif any(word in task_lower for word in ['класс', 'class']):
            entity_type = "class"
        elif any(word in task_lower for word in ['endpoint', 'маршрут', 'route', 'api']):
            entity_type = "endpoint"
        elif any(word in task_lower for word in ['файл', 'file']):
            entity_type = "file"
        elif any(word in task_lower for word in ['переменная', 'variable', 'config']):
            entity_type = "variable"
        else:
            entity_type = "function"
        
        # Извлекаем имя
        name = self._extract_name(task)
        
        return {
            "operation": operation,
            "entity_type": entity_type,
            "name": name,
            "description": task
        }
    
    def _extract_name(self, task: str) -> str:
        """Извлекает имя функции/класса из задачи"""
        # Ищем слова в кавычках
        quoted = re.findall(r'["\']([^"\']+)["\']', task)
        if quoted:
            return quoted[0]
        
        # Ищем слова после "функция", "класс" и т.д.
        patterns = [
            r'(?:функцию|функция|function)\s+(\w+)',
            r'(?:класс|class)\s+(\w+)',
            r'(?:переменную|variable)\s+(\w+)',
            r'(?:создай|добавь)\s+(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Генерируем имя по умолчанию
        return f"auto_{datetime.now().strftime('%H%M%S')}"
    
    def generate_code(self, analysis: Dict, existing_code: str = "") -> str:
        """Генерирует код на основе анализа"""
        entity_type = analysis["entity_type"]
        name = analysis["name"]
        description = analysis["description"]
        
        if entity_type == "function":
            return self._generate_function(name, description)
        elif entity_type == "class":
            return self._generate_class(name, description)
        elif entity_type == "endpoint":
            return self._generate_endpoint(name, description)
        elif entity_type == "variable":
            return self._generate_variable(name, description)
        else:
            return self._generate_function(name, description)
    
    def _generate_function(self, name: str, description: str) -> str:
        """Генерирует функцию Python"""
        # Определяем параметры из описания
        params = []
        if 'принимает' in description.lower() or 'принимает' in description:
            param_match = re.search(r'принимает\s+(\w+)', description)
            if param_match:
                params.append(param_match.group(1))
        
        params_str = ', '.join(params) if params else ''
        
        # Определяем возвращаемое значение
        return_value = 'None'
        if 'возвращает' in description.lower():
            return_value = 'result'
        
        body = f'    # {description}\n    result = None\n    return {return_value}'
        
        return self.templates["python_function"].format(
            function_name=name,
            params=params_str,
            description=description,
            body=body
        )
    
    def _generate_class(self, name: str, description: str) -> str:
        """Генерирует класс Python"""
        init_params = 'self'
        init_body = '        pass'
        
        methods = f"""
    def process(self):
        \"\"\"Основной метод класса\"\"\"
        pass
"""
        
        return self.templates["python_class"].format(
            class_name=name,
            description=description,
            params=init_params,
            init_body=init_body,
            methods=methods
        )
    
    def _generate_endpoint(self, name: str, description: str) -> str:
        """Генерирует Flask endpoint"""
        route = f'/{name.replace("_", "-")}'
        methods = 'GET'
        
        body = f'    # {description}\n    return {{"status": "ok", "message": "{description}"}}'
        return_value = 'jsonify(result)'
        
        return self.templates["flask_endpoint"].format(
            route=route,
            methods=methods,
            function_name=name,
            description=description,
            body=body,
            return_value=return_value
        )
    
    def _generate_variable(self, name: str, description: str) -> str:
        """Генерирует переменную"""
        # Определяем значение из описания
        value = 'None'
        
        if 'true' in description.lower():
            value = 'True'
        elif 'false' in description.lower():
            value = 'False'
        elif 'число' in description.lower() or 'number' in description.lower():
            value = '0'
        elif 'строка' in description.lower() or 'string' in description.lower():
            value = f'"{name}"'
        
        return f'{name} = {value}  # {description}'
    
    def modify_code(self, existing_code: str, task: str, analysis: Dict) -> str:
        """Модифицирует существующий код"""
        lines = existing_code.split('\n')
        
        # Ищем место для вставки
        if analysis["entity_type"] == "function":
            # Находим конец файла или другой функции
            insert_pos = len(lines)
            for i, line in enumerate(reversed(lines)):
                if line.strip().startswith('def ') and i < len(lines) - 1:
                    insert_pos = len(lines) - i
                    break
            
            new_code = self.generate_code(analysis, existing_code)
            lines.insert(insert_pos, new_code)
        
        return '\n'.join(lines)


class CodeAgent:
    def __init__(self, project_path: str, provider: str = "builtin"):
        self.project_path = Path(project_path).resolve()
        self.provider = provider
        self.builtin_ai = BuiltInAI()
        logger.info(f"✅ Инициализирован CodeAgent с провайдером: {provider}")
    
    def read_file(self, file_path: str) -> Optional[str]:
        """Читает файл из проекта"""
        full_path = self.project_path / file_path
        if full_path.exists() and full_path.is_file():
            try:
                return full_path.read_text(encoding='utf-8')
            except Exception as e:
                logger.error(f"Ошибка чтения {file_path}: {e}")
                return None
        return None
    
    def write_file(self, file_path: str, content: str) -> bool:
        """Записывает изменения в файл"""
        try:
            full_path = self.project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Создаём бэкап
            backup_path = full_path.with_suffix(f"{full_path.suffix}.backup")
            if full_path.exists():
                full_path.rename(backup_path)
                logger.info(f"💾 Создан бэкап: {backup_path}")
            
            # Записываем новый файл
            full_path.write_text(content, encoding='utf-8')
            logger.info(f"✅ Изменён файл: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка записи {file_path}: {e}")
            return False
    
    def get_project_structure(self, max_files: int = 20) -> List[str]:
        """Получает структуру проекта"""
        files = []
        extensions = ['.py', '.js', '.html', '.css', '.json', '.txt', '.md']
        
        for ext in extensions:
            for file_path in self.project_path.rglob(f"*{ext}"):
                if 'venv' not in str(file_path) and '__pycache__' not in str(file_path):
                    rel_path = file_path.relative_to(self.project_path)
                    files.append(str(rel_path))
                    if len(files) >= max_files:
                        break
            if len(files) >= max_files:
                break
        
        return files
    
    def find_best_file(self, task: str, structure: List[str]) -> str:
        """Находит наиболее подходящий файл для изменений"""
        task_lower = task.lower()
        
        # Приоритеты файлов
        priorities = {
            'app.py': 10,
            'main.py': 9,
            'server.py': 8,
            'bot.py': 7,
            'utils.py': 6,
            'helpers.py': 5,
            'config.py': 5
        }
        
        best_file = None
        best_score = -1
        
        for file in structure:
            score = 0
            # Проверяем по приоритету
            for pattern, priority in priorities.items():
                if pattern in file.lower():
                    score += priority
            
            # Проверяем по совпадению с задачей
            if any(word in file.lower() for word in task_lower.split()):
                score += 3
            
            if score > best_score:
                best_score = score
                best_file = file
        
        # Если ничего не нашли, берем первый .py файл
        if not best_file:
            py_files = [f for f in structure if f.endswith('.py')]
            best_file = py_files[0] if py_files else 'new_file.py'
        
        return best_file
    
    async def execute_task(self, task: str) -> Dict:
        """Основной метод выполнения задачи с встроенным AI"""
        logger.info(f"🧠 Анализирую задачу: {task}")
        
        # Получаем структуру проекта
        structure = self.get_project_structure()
        
        # Находим подходящий файл
        target_file = self.find_best_file(task, structure)
        
        # Читаем существующий код
        existing_code = self.read_file(target_file) or ""
        
        # Анализируем задачу встроенным AI
        analysis = self.builtin_ai.analyze_task(task, existing_code[:1000])
        
        logger.info(f"📊 Анализ: {analysis}")
        
        # Генерируем или модифицируем код
        if analysis["operation"] == "create":
            new_code = self.builtin_ai.generate_code(analysis, existing_code)
            if existing_code:
                # Добавляем в конец существующего файла
                new_code = existing_code + "\n\n# Новое: " + task + "\n" + new_code
        elif analysis["operation"] == "modify":
            new_code = self.builtin_ai.modify_code(existing_code, task, analysis)
        else:
            new_code = existing_code
        
        # Формируем результат
        result = {
            "files": [
                {
                    "path": target_file,
                    "content": new_code
                }
            ],
            "description": f"{analysis['operation'].capitalize()} {analysis['entity_type']} '{analysis['name']}': {task}",
            "analysis": analysis
        }
        
        # Если нужно создать новый файл
        if target_file == 'new_file.py' and not self.read_file(target_file):
            result["files"][0]["path"] = f"auto_{analysis['name']}.py"
        
        logger.info(f"✨ Сгенерированы изменения для {result['files'][0]['path']}")
        
        return result
    
    def apply_changes(self, changes: Dict) -> List[str]:
        """Применяет изменения к файлам"""
        modified_files = []
        
        if "error" in changes:
            logger.error(f"Ошибка в изменениях: {changes['error']}")
            return []
        
        for file_change in changes.get("files", []):
            path = file_change.get("path")
            content = file_change.get("content")
            
            if path and content:
                if self.write_file(path, content):
                    modified_files.append(path)
        
        return modified_files
    
    def rollback(self, file_path: str) -> bool:
        """Откат изменений из бэкапа"""
        full_path = self.project_path / file_path
        backup_path = full_path.with_suffix(f"{full_path.suffix}.backup")
        
        if backup_path.exists():
            backup_path.rename(full_path)
            logger.info(f"🔄 Откачен файл: {file_path}")
            return True
        return False