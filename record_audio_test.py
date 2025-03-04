from obswebsocket import obsws, requests
import time

# Параметры подключения к OBS WebSocket
host = "localhost"
port = 4455
password = "jXy9RT0qcKs93U83"

input_processes = ["msedge.exe"]

# Имя сцены для аудио-транскрипции
scene_name = "audio_transcriber_scene"

# Название источника для аудио-захвата
input_name = "Win Capture Audio"

ws = obsws(host, port, password)
ws.connect()


# Получаем список сцен
scenes_response = ws.call(requests.GetSceneList())
scenes = scenes_response.getScenes()

if not any(scene["sceneName"] == scene_name for scene in scenes):  
    raise ValueError("Сцены нет!!!")
else:
    print(f"Сцена '{scene_name}' уже существует.")

# Устанавливаем сцену как текущую
ws.call(requests.SetCurrentProgramScene(sceneName=scene_name))
print(f"Текущая сцена установлена: '{scene_name}'.")

# Начинаем запись
ws.call(requests.StartRecord())
print("Запись началась.")

# Записываем в течение 10 секунд
time.sleep(10)

ws.call(requests.StopRecord())
print("Запись остановлена.")

ws.disconnect()
