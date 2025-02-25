from typing import List
import subprocess
import pefile
import ctypes
import os

class DllLoader():
    def __init__(self, dll_relative_directories: List[str] = []):
        for directory in dll_relative_directories:
            self.add_relative_dll_directory(directory)

    def add_dll_directory(self, directory: str):
        os.add_dll_directory(directory)
    
    def add_relative_dll_directory(self, relative_directory: str):
        os.add_dll_directory(os.path.join(os.getcwd(), relative_directory))

    def get_dll_dependencies(self, dll_path):
        try:
            pe = pefile.PE(dll_path)
            return [entry.dll.decode() for entry in pe.DIRECTORY_ENTRY_IMPORT]
        except Exception as e:
            print(f"Ошибка анализа {dll_path}: {e}")
            return []

    def find_dll_directory(self, dll_name):
        try:
            output = subprocess.check_output(["where", dll_name], shell=True, universal_newlines=True)
            paths = output.strip().splitlines()
            if paths:
                return os.path.dirname(paths[0])
        except subprocess.CalledProcessError:
            return None

    def is_dll_loadable(self, dll_path):
        try:
            ctypes.WinDLL(dll_path)
            return True
        except OSError:
            system_dll_directory = self.find_dll_directory(dll_path)
            if system_dll_directory is None:
                return False

            os.add_dll_directory(system_dll_directory)
            try:
                dll_name = os.path.basename(dll_path)
                system_dll_path = os.path.join(system_dll_directory, dll_name)

                ctypes.WinDLL(system_dll_path)
                return True
            except OSError:
                return False

    def load_dll(self, dll_path, show_errors=True):
        try:
            dll = ctypes.WinDLL(dll_path)
            return dll
        except OSError:
            pass 

        dependencies = self.get_dll_dependencies(dll_path)
        if not dependencies:
            if not show_errors:
                return None
            raise OSError("Не удалось получить список зависимостей.")
        
        missing_dependencies = []
        for dep in dependencies:
            dep_dir = self.find_dll_directory(dep)
            dep_path = os.path.join(dep_dir, dep) if dep_dir is not None else dep
            if not self.is_dll_loadable(dep_path):
                if self.load_dll(dep_path, show_errors=False) is None:
                    missing_dependencies.append(dep)
        
        if len(missing_dependencies) == 0:
            dll = ctypes.WinDLL(dll_path)
            return dll
        else:
            if not show_errors:
                return None
            raise OSError("Не удалось загрузить библиотеку из-за недостающих зависимостей. Отсутствуют следующие библиотеки:\n" + '\n'.join(missing_dependencies))