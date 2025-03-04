// return new Promise(resolve => {
//     chrome.storage.local.get("instance_id", (result) => {
//         if (chrome.runtime.lastError) {
//             console.error("Ошибка при получении instance_id:", chrome.runtime.lastError);
//         }
//         if (result && result.instance_id) {
//             console.log("Уникальный instance_id уже был:", result.instance_id);
//             resolve(result.instance_id);
//         } else {
//             let instance_id_uuid = crypto.randomUUID();
//             chrome.storage.local.set({ instance_id: instance_id_uuid }, () => {
//                 console.log("Уникальный ID сохранен:", instance_id_uuid);
//                 resolve(instance_id_uuid);
//             });
//         }
//     });
// });

return new Promise(resolve => {
    // Получаем или генерируем instance_id
    let instance_id_uuid = crypto.randomUUID();

    // Отправляем ID в расширение через message API
    window.postMessage({ type: "set_instance_id", instance_id: instance_id_uuid }, "*");
    console.log('ID передан в расширение:', instance_id_uuid);
    
    resolve(instance_id_uuid)
});