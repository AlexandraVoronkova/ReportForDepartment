$(document).ready(function () {
    let cookiemessage = localStorage.getItem('cookiemessage');
    let cookie_div = document.getElementsByClassName('bottom_cookie-block')[0];
    // проверяем, есть ли у нас запись в localStorage, с которой мы не показываем окно и если нет, запускаем показ
    if (cookiemessage != "no") {
        cookie_div.style.display = "inline-block";
        // закрываем по клику
        document.getElementById("cookie_close").addEventListener("click", function () {
            cookie_div.style.display = "none";
            localStorage.setItem('cookiemessage', 'no');
        });
    }
});
