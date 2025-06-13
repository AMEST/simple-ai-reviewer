from dataclasses import fields
import json
import logging

from contracts.per_file_review_result import PerFileReviewResult
from services.ai.ai_client import AIClient
from configuration.review_configuration import ReviewConfiguration, Language
from configuration.llm_configuration import LLMConfiguration

from utils.diff_utils import split_diff, get_files_from_diff, get_changed_lines
from utils.text_utils import extract_json_blocks

class ReviewService:
    """
    Service for performing code reviews using AI.
    
    This service analyzes pull request diffs and provides code review feedback
    using an AI client. Supports both Russian and English languages.
    
    Attributes:
        configuration (ReviewConfiguration): Configuration for review settings
        llm_configuration (LLMConfiguration): Configuration for the language model
        ai_client (AIClient): The AI client used for generating reviews
        logger (logging.Logger): Logger instance for service operations
    """
    def __init__(self, configuration: ReviewConfiguration, llm_configuration: LLMConfiguration, ai_client : AIClient):
        """
        Initialize the ReviewService with configurations and AI client.
        
        Args:
            configuration (ReviewConfiguration): Configuration for review settings
            llm_configuration (LLMConfiguration): Configuration for the language model
            ai_client (AIClient): The AI client to use for generating reviews
        """
        self.configuration = configuration
        self.llm_configuration = llm_configuration
        self.ai_client = ai_client
        self.logger = logging.getLogger(ReviewService.__name__)
        self.system_prompt = {
            "role":"system", 
            "content": "Ты инженер-программист с обширными знаниями, ты должен помочь провести ревью предложенного кода и выдать свой вердикт как попросил пользователь. Отвечать нужно строго на Русском Языке и в том формате, который требуют (если не указан, то в любом формате)!" if self.configuration.language == Language.RU else "You are a software engineer with extensive knowledge, you must help review the proposed code and give your verdict as requested by the user. You must answer strictly in English and in the format that is required (if not specified, then in any format)!"
        }

    @property
    def is_comment_review_enabled(self):
        return self.configuration.review_as_comments
    
    @property
    def is_conversation_review_enabled(self):
        return self.configuration.review_as_conversations

    def review_pull_request(self, diff: str, user_message: str = None) -> list[str]:
        """
        Perform a code review on a pull request diff.
        
        Args:
            diff (str): The git diff content to review
            user_message (str, optional): Additional instructions from the user
            
        Returns:
            list[str]: List of review results, one for each diff chunk
        """
        results = []
        splited_diff = split_diff(diff, 12000, self.configuration.ignore_files)
        self.logger.info(f"Received diff (len = {len(diff)}) for automatic review. Split to {len(splited_diff)} diffs")
        for diff_slice in splited_diff:
            file_names = "\n* ".join(get_files_from_diff(diff_slice))
            prompt = self.__en_prompt(diff_slice, user_message) if self.configuration.language == Language.EN else self.__ru_prompt(diff_slice, user_message)
            review_result = self.ai_client.completions([self.system_prompt, {"role":"user","content":prompt}], self.llm_configuration.model)
            results.append(f"🤖 AI Code Review:\n\nFiles: \n* {file_names}\n\n{review_result}")
        return results

    def per_file_review_pull_request(self, diff: str) -> list[PerFileReviewResult]:
        """
        Perform a per file code review on a pull request diff.
        
        Args:
            diff (str): The git diff content to review
            
        Returns:
            list[dict]: List of review results, one for each diff chunk
        """
        results = []
        changed_lines = get_changed_lines(diff)
        splited_diff = split_diff(diff, 12000, self.configuration.ignore_files)
        self.logger.info(f"Received diff (len = {len(diff)}) for automatic per file review. Split to {len(splited_diff)} diffs")
        for diff_slice in splited_diff:
            prompt = self.__en_per_file_prompt(diff_slice) if self.configuration.language == Language.EN else self.__ru_per_file_prompt(diff_slice)
            review_result = self.ai_client.completions([self.system_prompt, {"role":"user","content":prompt}], self.llm_configuration.model)
            json_in_result = extract_json_blocks(review_result)
            if len(json_in_result) == 0:
                self.logger.warning("Json not found in per file review!\n%s", review_result)
                continue
            for result in json.loads(json_in_result[0]):
                if not isinstance(result, dict):
                    continue
                review_result_fields = {f.name for f in fields(PerFileReviewResult)}
                per_file_result = PerFileReviewResult(**{k: v for k, v in result.items() if k in review_result_fields})
                changed_lines_in_file : list[int] = changed_lines.get(per_file_result.path)
                if changed_lines_in_file is None:
                    continue
                added_lines = changed_lines_in_file.get("added")
                removed_lines = changed_lines_in_file.get("removed")
                if len(added_lines) > 0:
                    per_file_result.line = min(added_lines, key=lambda x: abs(x - (per_file_result.line + 1)))
                elif len(removed_lines) > 0:
                    per_file_result.line = min(removed_lines, key=lambda x: abs(x - (per_file_result.line + 1)))
                else:
                    continue
                results.append(per_file_result)
        return results

    def __ru_prompt(self, diff: str, user_message: str) -> str:
        """
        Generate a Russian language prompt for the AI review.
        
        Args:
            diff (str): The git diff content to review
            user_message (str): Additional instructions from the user
            
        Returns:
            str: Formatted prompt in Russian
        """
        return f"""Проанализируй изменения в коде (в формате diff из git):
```
{diff}
```

Проверь:
0. Ничего не пиши про diff (изменения в нем, сам формат, описание изменений), изменения представлены в данном формате только для удобств анализа
1. Стиль кода (который соответствует языку программирования в файле)
2. Потенциальные баги
3. Уязвимости безопасности
4. Возможности рефакторинга
5. Отвечай на русском языке
{f"Дополнительное условие от пользователя: {user_message}" if user_message is not None else ""}

Ответ оформи в виде списка с метками: ✅ Плюсы,⚠️ Проблемы,💡 Советы{f", 🙎‍♂️ответ на дополнительное условие пользователя" if user_message is not None else ""}
"""
    
    def __en_prompt(self, diff: str, user_message: str) -> str:
        """
        Generate an English language prompt for the AI review.
        
        Args:
            diff (str): The git diff content to review
            user_message (str): Additional instructions from the user
            
        Returns:
            str: Formatted prompt in English
        """
        return f"""Analyze the changes in the code (in diff format from git):
```
{diff}
```

Check:
0. Do not write anything about the diff (changes in it, the format itself, description of changes), the changes are presented in this format only for the convenience of analysis
1. Code style (which corresponds to the programming language in the file)
2. Potential bugs
3. Security vulnerabilities
4. Refactoring opportunities
5. Answer in English language
{f"Additional condition from the user: {user_message}" if user_message is not None else ""}

Format your answer as a list with tags: ✅ Pros, ⚠️ Problems, 💡 Tips{f", 🙎‍♂️response to additional user condition" if user_message is not None else ""}
"""


    def __ru_per_file_prompt(self, diff: str) -> str:
        """
        Generate an Russian language prompt for the per file AI review.
        
        Args:
            diff (str): The git diff content to review
            
        Returns:
            str: Formatted prompt in Russian
        """
        return f"""Проанализируйте следующий вывод git diff и предоставьте конкретные предложения по улучшению в строгом формате JSON:

```diff
{diff}
```
Выполнить подробный анализ каждого измененного файла на предмет:

1. Ошибок (синтаксических/логических)
2. Нарушений стиля кода (специфичных для языка)
3. Потенциальных ошибок
4. Уязвимостей безопасности и утечек ресурсов

Для каждой найденной проблемы предоставьте:
1. Четкое описание
2. Конкретный номер строки из diff (используйте точный номер строки, где необходимо изменение)
3. Предлагаемое исправление кода

Выведите ТОЛЬКО массив JSON, соответствующий этой точной структуре:
[
{{
"path": "full/file/path/from/diff/header",
"line": INTEGER, // MUST use the line number from diff context
"body": "Description of issue and suggested fix (with code suggestion if applicable)"
}},
...
]

Важно:
1. Номера строк ДОЛЖНЫ соответствовать фактическим номерам строк в diff
2. Включайте только элементы, требующие действий, с определенными местоположениями
3. Никогда не добавляйте комментарии вне структуры JSON
4. Для перемещенных/переименованных файлов используйте конечный путь из diff
5. Для многострочных изменений укажите конечный номер строки
"""

    def __en_per_file_prompt(self, diff: str) -> str:
        """
        Generate an English language prompt for the per file AI review.
        
        Args:
            diff (str): The git diff content to review
            
        Returns:
            str: Formatted prompt in English
        """
        return f"""Analyze the following git diff output and provide specific improvement suggestions in strict JSON format:

```diff
{diff}
```
Perform detailed analysis of each changed file for:

1. Errors (syntax/logical)
2. Code style violations (language-specific)
3. Potential bugs
4. Security vulnerabilities and resource leaks

For each issue found, provide:
1. Clear description
2. Specific line number from the diff (use the exact line number where change is needed)
3. Suggested code fix

Output ONLY a JSON array following this exact structure:
[
{{
"path": "full/file/path/from/diff/header",
"line": INTEGER, // MUST use the line number from diff context
"body": "Description of issue and suggested fix (with code suggestion if applicable)"
}},
...
]

Important:
1. Line numbers MUST correspond to the actual line numbers in the diff
2. Include only actionable items with specific locations
3. Never add comments outside JSON structure
4. For moved/renamed files, use final path from diff
5. For multiline changes, reference ending line number
"""