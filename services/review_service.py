import logging

from services.ai.ai_client import AIClient
from configuration.review_configuration import ReviewConfiguration, Language
from configuration.llm_configuration import LLMConfiguration

from utils.diff_utils import split_diff, get_files_from_diff

class ReviewService:
    def __init__(self, configuration: ReviewConfiguration, llm_configuration: LLMConfiguration, ai_client : AIClient):
        self.configuration = configuration
        self.llm_configuration = llm_configuration
        self.ai_client = ai_client
        self.logger = logging.getLogger(ReviewService.__name__)

    def review_pull_request(self, diff: str, user_message: str = None) -> list[str]:
        results = []
        splited_diff = split_diff(diff, 12000)
        self.logger.info(f"Received diff (len = {len(diff)}) for automatic review. Split to {len(splited_diff)} diffs")
        for diff_slice in splited_diff:
            file_names = "\n* ".join(get_files_from_diff(diff_slice))
            prompt = self.__en_prompt(diff_slice, user_message) if self.configuration.language == Language.EN else self.__ru_prompt(diff_slice, user_message)
            review_result = self.ai_client.completions([{"role":"user","content":prompt}], self.llm_configuration.model)
            results.append(f"🤖 AI Code Review:\n\nFiles: \n* {file_names}\n\n{review_result}")
        return results

    def __ru_prompt(self, diff: str, user_message: str) -> str:
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