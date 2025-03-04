// background.js
let mediaRecorder;
let audioChunks = [];
const server_url = "http://127.0.0.1:8989/";
let botId = -1; // Будет получен из chrome.storage
let instance_id = "";
const pooling_interval = 1000; // Интервал пулинга в мс

// Получаем botId из настроек (если не установлен, по умолчанию 0)
(async () => {
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "set_instance_id") {
      instance_id = message.instance_id;
      console.log("Получен instance_id: ", instance_id);
    }
  });

  chrome.tabCapture.capture({ audio: true, video: false }, (stream) => {})

  setInterval(pollCommands, (pooling_interval));

})();

// async function ensureOffscreenDocument() {
//   const hasDocument = await chrome.offscreen.hasDocument();
//   if (!hasDocument) {
//     await chrome.offscreen.createDocument({
//       url: 'offscreen.html',
//       reasons: ['AUDIO_PLAYBACK'],
//       justification: 'Нужен DOM для захвата аудио из вкладки.'
//     });
//   }
// }

// async function ensureOffscreenDocument() {
//   console.log("Проверяем, есть ли offscreen-документ...");
//   const hasDocument = await chrome.offscreen.hasDocument();
//   console.log("hasDocument =", hasDocument);
//   if (!hasDocument) {
//     console.log("Offscreen-документ отсутствует. Создаём...");
//     await chrome.offscreen.createDocument({
//       url: 'offscreen.html',
//       reasons: ['AUDIO_PLAYBACK'],
//       justification: 'Нужен DOM для захвата аудио из вкладки.'
//     });
//     console.log("Offscreen-документ создан.");
//   } else {
//     console.log("Offscreen-документ уже существует.");
//   }
// }

async function startRecording(data) {
  if (data.event && data.event.happened) {
    // chrome.runtime.sendMessage({ type: 'start_recording', save_path: data.event.save_path });

    // // Если запись не идёт, запускаем её
    // if (!mediaRecorder || mediaRecorder.state === "inactive") {
    //   let save_path = data.event.save_path
    //   chrome.tabCapture.capture({ audio: true, video: false }, (stream) => {
    //     if (!stream) {
    //       console.error("Не удалось захватить аудио вкладки.");
    //       return;
    //     }
    //     mediaRecorder = new MediaRecorder(stream);
    //     audioChunks = [];

    //     mediaRecorder.ondataavailable = (event) => {
    //       if (event.data && event.data.size > 0) {
    //         audioChunks.push(event.data);
    //       }
    //     };

    //     mediaRecorder.onstop = () => {
    //       let blob = new Blob(audioChunks, { type: "audio/webm" });
    //       let url = URL.createObjectURL(blob);
    //       chrome.downloads.download({
    //         url: url,
    //         // Путь относительно стандартной папки загрузок (можно задать, например, "MyFolder/tab_audio.webm")
    //         filename: save_path
    //       }, (downloadId) => {
    //         console.log(`Запись завершена, файл сохранён (downloadId: ${downloadId}).`);
    //       });
    //     };

    //     mediaRecorder.start();
    //     console.log(`🔴 Бот ${botId} начал запись (сохранение в ${save_path}).`);
    //   });
    // }
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length === 0) {
        console.error("Нет активной вкладки для записи.");
        return;
      }

      chrome.scripting.executeScript({
        target: { tabId: tabs[0].id },
        function: (save_path) => {
          // Если запись не идёт, запускаем её
          if (!window.mediaRecorder || window.mediaRecorder.state === "inactive") {
            chrome.tabCapture.capture({ audio: true, video: false }, (stream) => {
              if (!stream) {
                console.error("Не удалось захватить аудио вкладки.");
                return;
              }
              window.mediaRecorder = new MediaRecorder(stream);
              window.audioChunks = [];
  
              window.mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) {
                  window.audioChunks.push(event.data);
                }
              };
  
              window.mediaRecorder.onstop = () => {
                let blob = new Blob(window.audioChunks, { type: "audio/webm" });
                let url = URL.createObjectURL(blob);
                chrome.downloads.download({
                  url: url,
                  // Путь относительно стандартной папки загрузок (можно задать, например, "MyFolder/tab_audio.webm")
                  filename: save_path
                }, (downloadId) => {
                  console.log(`Запись завершена, файл сохранён (downloadId: ${downloadId}).`);
                });
              };
  
              window.mediaRecorder.start();
              console.log(`🔴 Бот ${botId} начал запись (сохранение в ${save_path}).`);
            });
          }
        },
        args: [data.event.save_path]
      });
    });
  }
}

async function stopRecording(data) {
    if (data.event && data.event.happened) {
      // chrome.runtime.sendMessage({ type: 'stop_recording' });

      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.scripting.executeScript({
          target: { tabId: tabs[0].id },
          function: () => { 
            if (window.mediaRecorder && window.mediaRecorder.state !== "inactive") {
              window.mediaRecorder.stop();
              console.log(`🛑 Бот ${botId} остановил запись.`);
              window.myMediaRecorder = null;
            }
          }
      });
    });
  }
}

async function recive_bot_id(data) {
  if (data.event && data.event.happened) {
    botId = parseInt(data.event.bot_id, 10);
    console.log("bot_id получен и равен: ", botId);
  }
}

async function pollUrl(url, callback) {
  try {
    let response = await fetch(url, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      keepalive: true
    });
    if (!response.ok) {
      throw new Error(`Ошибка HTTP при polling start: ${response.status}`);
    }
    let data = await response.json();
    callback(data);
  } catch (error) {
    console.error("⚠ Ошибка запроса polling start:", error);
  }
}

async function pollCommands() {
  // Опрос команды на запуск записи
  if (botId >= 0) {
    // await pollUrl(server_url + "start_recording_pooling/" + botId, startRecording);
    // await pollUrl(server_url + "stop_recording_pooling/" + botId, stopRecording);
  } else {
    if (instance_id.length > 0)
      await pollUrl(server_url + "recive_bot_id/" + instance_id, recive_bot_id);
  }
}
