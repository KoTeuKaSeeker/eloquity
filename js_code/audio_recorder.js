(async () => {
    let mediaRecorder;
    let audioChunks = [];
    let server_url = [-SERVER_URL-];
    let botId = [-BOT_ID-]; // Уникальный ID для каждого бота
    let pooling_interval = [-POOLING_INTERVAL-] // 1000 мс = 1 сек

    const startRecording = async (save_path) => {
        let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            let audioBlob = new Blob(audioChunks, { type: "audio/wav" });
            let url = URL.createObjectURL(audioBlob);
            let a = document.createElement("a");
            a.href = url;
            a.download = save_path;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        };

        mediaRecorder.start();
        console.log(`🔴 Бот ${botId} начал запись`);
    };

    const stopRecording = async () => {
        if (mediaRecorder) {
            mediaRecorder.stop();
            console.log(`🛑 Бот ${botId} остановил запись`);
        }
    };

    const poolingStartRecording = async () => {
        let url = server_url + "start_recording_pooling/" + botId;

        try {
            let response = await fetch(url, {
                method: "GET",
                headers: { "Content-Type": "application/json" }
            });

            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }

            let data = await response.json();
            if (data.event?.happened) {
                startRecording(data.event.save_path);
            }
        } catch (error) {
            console.error("⚠ Ошибка запроса:", error);
        }
    };

    const poolingStopRecording = async () => {
        let url = server_url + "stop_recording_pooling/" + botId;

        try {
            let response = await fetch(url, {
                method: "GET",
                headers: { "Content-Type": "application/json" }
            });

            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }

            let data = await response.json();
            if (data.event?.happened) {
                stopRecording();
            }
        } catch (error) {
            console.error("⚠ Ошибка запроса:", error);
        }
    };

    // ✅ Запуск пулинга раз в секунду
    setInterval(poolingStartRecording, pooling_interval);
    setInterval(poolingStopRecording, pooling_interval);
})();
