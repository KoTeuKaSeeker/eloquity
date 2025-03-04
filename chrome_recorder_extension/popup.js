// let mediaRecorder;
// let audioChunks = [];

// document.getElementById("start").addEventListener("click", async () => {
//   // Запускаем захват аудио текущей вкладки
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
//       // Сохраняем файл через API downloads
//       chrome.downloads.download({
//         url: url,
//         filename: "tab_audio.webm"
//       });
//       console.log("Запись завершена, файл сохранён.");
//     };

//     mediaRecorder.start();
//     console.log("Запись начата.");
//     document.getElementById("start").disabled = true;
//     document.getElementById("stop").disabled = false;
//   });
// });

// document.getElementById("stop").addEventListener("click", () => {
//   if (mediaRecorder && mediaRecorder.state !== "inactive") {
//     mediaRecorder.stop();
//     document.getElementById("start").disabled = false;
//     document.getElementById("stop").disabled = true;
//   }
// });
