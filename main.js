console.log('Hello world!')

const ws = new WebSocket('ws://localhost:8080')  // connect to the web socket (створюємо новий клас WebSocket)

formChat.addEventListener('submit', (e) => { // Обробляємо подію submit форми при натисканні кнопки (прослуховувач подій)
    e.preventDefault()  // Зупиняємо стандартну обробку форми, щоб браузер не надіслав повідомлення самостійно
    ws.send(textField.value)  // Надсилаємо повідомлення самостійно на сервер, де textField.value значення інпута <input type="text" id="textField"/>
    textField.value = null  // Обнулюємо поле введення командою textField.value = null.
})

// Створюємо функцію (при під'єднанні) за подією onopen
ws.onopen = (e) => {  // Виводимо вітальне повідомлення до консолі браузера при з'єднанні з веб-сокетом:
    console.log('Hello WebSocket!')
}

/*
Цей код спрацьовує, коли сервер надсилає повідомлення клієнту методом send_to_clients. 
Він отримує повідомлення від веб-сокету (e.data ) та додає його в DOM дерево веб сторінки:
*/
ws.onmessage = (e) => {  // подія onmessage на веб-сокеті
    console.log(e.data)  // треба знати що в JS приходить e.data 
    text = e.data

    // Виводимо на сторінку браузера отримане повідомлення:
    const elMsg = document.createElement('div')
    elMsg.textContent = text
    subscribe.appendChild(elMsg)
}
