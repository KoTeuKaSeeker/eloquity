import os
import ctypes
import pefile
import subprocess


def find_dll_directory(dll_name):
    try:
        output = subprocess.check_output(["where", dll_name], shell=True, universal_newlines=True)
        paths = output.strip().splitlines()
        if paths:
            return os.path.dirname(paths[0])
    except subprocess.CalledProcessError:
        return None


def is_dll_loadable(dll_path):
    """Проверяет, можно ли загрузить DLL."""
    try:
        ctypes.WinDLL(dll_path)
        return True
    except OSError:
        system_dll_path = find_dll_directory(dll_path)
        if system_dll_path is None:
            return False
        os.add_dll_directory(system_dll_path)
        try:
            ctypes.WinDLL(system_dll_path)
            return True
        except OSError:
            return False

def get_dll_dependencies(dll_path):
    """Возвращает список зависимостей DLL."""
    try:
        pe = pefile.PE(dll_path)
        return [entry.dll.decode() for entry in pe.DIRECTORY_ENTRY_IMPORT]
    except Exception as e:
        print(f"Ошибка анализа {dll_path}: {e}")
        return []

def find_dll_in_system(dll_name):
    """Проверяет наличие DLL в стандартных папках."""
    system_paths = [r"C:\Windows\System32", r"C:\Windows\SysWOW64"]
    for path in system_paths:
        full_path = os.path.join(path, dll_name)
        if os.path.exists(full_path):
            return full_path
    return None

def check_missing_dependencies(dll_path):
    """Проверяет и выводит отсутствующие зависимости."""
    print(f"🔍 Проверка DLL: {dll_path}")

    dependencies = get_dll_dependencies(dll_path)
    if not dependencies:
        print("⚠ Не удалось получить список зависимостей.")
        return
    
    missing = []
    print("\n📌 Список зависимостей:")
    for dep in dependencies:
        dep_dir = find_dll_directory(dep)
        dep_path = os.path.join(dep_dir, dep) if dep_dir is not None else dep
        if dep_path and is_dll_loadable(dep_path):
            print(f"  ✅ {dep} (найдена: {dep_path})")
        else:
            print(f"  ❌ {dep} (отсутствует или не загружается!)")
            missing.append(dep)

    if missing:
        print("\n🚨 Отсутствующие зависимости:")
        for dep in missing:
            print(f"  ❌ {dep}")
        print("\n❌ Основная DLL не загружается!")
    else:
        print("\n✅ Основная DLL загружается без ошибок!")

# Укажи путь к своей DLL
dll_path = "bin/win-capture-audio.dll"

if __name__ == "__main__":
    os.add_dll_directory(os.path.join(os.getcwd(), "bin"))
    check_missing_dependencies(dll_path)