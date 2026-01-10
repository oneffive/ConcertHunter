# ConcertHunter

Агрегатор концертных анонсов для любителей музыки с целью покупки билетов в определённом городе. **ConcertHunter** решает проблему ручного поиска билетов: вы просто подписываетесь на любимых артистов в нужных городах, а система сама отслеживает афиши через глобальный API и визуализирует предстоящие события на интерактивной карте.

**Рабочий проект:** [https://ktoto40k.pythonanywhere.com/](https://ktoto40k.pythonanywhere.com/)

---

## Стек технологий

*   **Backend:** Python 3.10, Django 5.0
*   **External API:** Ticketmaster Discovery API (поиск артистов и событий)
*   **Frontend:** Bootstrap 5 (UI/UX), HTML5, CSS3
*   **Geolocation & Maps:** Leaflet.js + OpenStreetMap (интерактивная карта)
*   **Data Processing:**
    *   `requests` — для работы с внешним API
    *   `deep-translator` — для автоматического перевода и нормализации названий городов (решение проблемы "İstanbul" vs "Istanbul")
    *   `unicodedata` — очистка текста от диакритических знаков

---

##  Интерфейс и возможности

### 1. Личный кабинет и карта
Главная страница пользователя, содержащая список отслеживаемых концертов и интерактивную карту с их географическим расположением.

<img width="893" height="796" alt="image (5)" src="https://github.com/user-attachments/assets/5ea402ac-ac33-4d88-b99d-89546394714e" />


### 2. Умный поиск и подписка
Страница поиска артистов с возможностью подписки. Результаты загружаются из глобальной базы Ticketmaster, каждая позиция доступна для добавления в список отслеживаемых исполнителей.

<img width="1915" height="917" alt="image (4)" src="https://github.com/user-attachments/assets/5c0939c4-39d0-489f-90da-30cadd4c8c54" />


---

## Как запустить проект локально

Если вы хотите развернуть проект на своем компьютере, следуйте инструкции:

### 1. Клонируйте репозиторий:
```bash
git clone https://github.com/oneffive/ConcertHunter.git
cd ConcertHunter
```

### 2. Создайте и активируйте виртуальное окружение:

#### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установите зависимости:
```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения:
1. Создайте файл `.env` в корне проекта
2. Добавьте ваш API-ключ (получить можно на [developer.ticketmaster.com](https://developer.ticketmaster.com)):

```
TM_API_KEY = ваш ключ от TicketMasterAPI
SECRET_KEY = ваша секретная строка django
DEBUG=True
```

Совет: чтобы сгенерировать новый надежный SECRET_KEY, вы можете выполнить эту команду в терминале:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 5. Выполните миграции:
```bash
python manage.py migrate
```

### 6. Наполните базу данных:
```bash
python manage.py update_events
```

### 7. Запустите сервер:
```bash
python manage.py runserver
```

### 8. Готово
Откройте в браузере: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
