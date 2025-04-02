from abc import ABC, abstractmethod
from typing import Dict, Callable, Any, List
import re

class LLMFunctionFactory():
    llm_functions: Dict[str, Callable[..., str]]

    def __init__(self):
        self.llm_functions = {}

    def set_llm_function(self, llm_function_name: str, llm_function: Callable[..., str]):
        self.llm_functions[llm_function_name] = llm_function

    def split_arguments(self, arg_str):
        """
        Разбивает строку аргументов на отдельные аргументы,
        корректно обрабатывая вложенные скобки и кавычки.
        """
        args = []
        current = []
        bracket_count = 0  # для учета вложенных скобок
        quote_char = None  # для отслеживания открытых кавычек (" или ')
        i = 0
        while i < len(arg_str):
            char = arg_str[i]
            if quote_char:
                current.append(char)
                # Если встречаем символ закрывающей кавычки, проверяем экранирование
                if char == quote_char:
                    j = i - 1
                    escaped = False
                    while j >= 0 and arg_str[j] == '\\':
                        escaped = not escaped
                        j -= 1
                    if not escaped:
                        quote_char = None
                i += 1
                continue
            else:
                if char in ('"', "'"):
                    quote_char = char
                    current.append(char)
                elif char == '(':
                    bracket_count += 1
                    current.append(char)
                elif char == ')':
                    if bracket_count > 0:
                        bracket_count -= 1
                    current.append(char)
                elif char == ',' and bracket_count == 0:
                    # Разделитель аргументов вне вложенных скобок
                    args.append(''.join(current).strip())
                    current = []
                else:
                    current.append(char)
            i += 1

        if current:
            args.append(''.join(current).strip())
        return args

    def extract_all_function_arguments_with_position(self, text, function_name):
        """
        Ищет все внешние вызовы функции с именем function_name в тексте и возвращает список словарей.
        Каждый словарь содержит:
        - 'start': позиция начала совпадения в тексте,
        - 'end': позиция конца совпадения,
        - 'arguments': список аргументов вызова функции.
        Вложенные вызовы воспринимаются как часть аргументов.
        """
        pattern = re.compile(fr"{function_name}\s*\(")
        results = []
        
        for match in pattern.finditer(text):
            start_match = match.start()  # начало совпадения функции
            start_args = match.end()       # позиция сразу после открывающей скобки
            bracket_count = 1
            i = start_args
            # Проходим по тексту, чтобы найти соответствующую закрывающую скобку для внешнего вызова
            while i < len(text) and bracket_count > 0:
                if text[i] == '(':
                    bracket_count += 1
                elif text[i] == ')':
                    bracket_count -= 1
                i += 1
            if bracket_count == 0:
                end_match = i  # позиция после закрывающей скобки
                args_str = text[start_args:i-1].strip()  # строка аргументов без внешних скобок
                args = self.split_arguments(args_str)
                results.append({
                    "start": start_match,
                    "end": end_match,
                    "arguments": args
                })
        return results

    def get_functions_queue_from_llm_mesasge(self, llm_message: str) -> List[dict]:
        all_functions_matches = []
        for function_name in self.llm_functions.keys():
            results = self.extract_all_function_arguments_with_position(llm_message, function_name)
            all_functions_matches += [{"start": result["start"], "end": result["end"], "function": self.llm_functions[function_name], "args": result["arguments"]} for result in results]
        
        sorted_all_functions_matches = sorted(all_functions_matches, key=lambda x: x["start"])

        return sorted_all_functions_matches

    def run_all_functions(self, llm_message: str) -> str:
        function_matches = self.get_functions_queue_from_llm_mesasge(llm_message)
        paste_texts = []
        for fucntion_match in function_matches:
            func = fucntion_match["function"]
            args = fucntion_match["args"]
            paste_text = func(llm_message, *args)
            paste_texts.append(paste_text, fucntion_match["start"], fucntion_match["end"])
        
        pointer = paste_texts[1]
        for paste_text in paste_texts:
            llm_message = llm_message[:paste_text[1]] + paste_text + llm_message[paste_text[2]:] 
            

            

    def get_llm_function(self, function_name) -> Callable[..., str]:
        return self.llm_functions[function_name]