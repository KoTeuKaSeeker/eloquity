console.log("Content script загружен!");
// let mediaRecorder = null;
// let audioChunks = [];
// let botId = -1;

window.addEventListener("message", (event) => {
    // Фильтруем сообщения, чтобы убедиться, что они отправлены с той же страницы
    if (event.source !== window) return;
    if (event.data && event.data.type === "set_instance_id") {
      // Отправляем сообщение в background script
      chrome.runtime.sendMessage({
        type: "set_instance_id",
        instance_id: event.data.instance_id
      });
    }
});

// chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
//     if (message.type === "start_recording") {
//         startRecording(message);
//     } else if (message.type === "stop_recording") {
//         stopRecording(message);
//     }
// });

// // Запуск записи
// async function startRecording(message) {
//     if (!mediaRecorder || mediaRecorder.state === "inactive") {
//         let save_path = message.save_path || "tab_audio.webm";

//         chrome.tabCapture.capture({ audio: true, video: false }, (stream) => {
//             if (!stream) {
//                 console.error("Не удалось захватить аудио вкладки.");
//                 return;
//             }

//             mediaRecorder = new MediaRecorder(stream);
//             audioChunks = [];

//             mediaRecorder.ondataavailable = (event) => {
//                 if (event.data && event.data.size > 0) {
//                     audioChunks.push(event.data);
//                 }
//             };

//             mediaRecorder.onstop = () => {
//                 let blob = new Blob(audioChunks, { type: "audio/webm" });
//                 let url = URL.createObjectURL(blob);
//                 chrome.downloads.download({
//                     url: url,
//                     filename: save_path
//                 }, (downloadId) => {
//                     console.log(`Запись завершена, файл сохранён (downloadId: ${downloadId}).`);
//                 });
//             };

//             mediaRecorder.start();
//             console.log(`🔴 Бот ${botId} начал запись (сохранение в ${save_path}).`);
//         });
//     }
// }

// // Остановка записи
// async function stopRecording(message) {
//     if (mediaRecorder && mediaRecorder.state !== "inactive") {
//         mediaRecorder.stop();
//         console.log(`🛑 Бот ${botId} остановил запись.`);
//     }
// }