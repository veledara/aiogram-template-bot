# veledara aiogram bot template

## Описание

Этот шаблон предоставляет основу для создания full-async Telegram бота с использованием [Aiogram](https://docs.aiogram.dev/) и [SQLAlchemy](https://www.sqlalchemy.org/).

## Установка

1. **Клонируйте репозиторий**

   ```bash
   git clone https://github.com/ваш-юзернейм/aiogram-bot-template.git
   cd aiogram-bot-template

2. **Установите Poetry**
    
    Если у вас еще не установлен [poetry](https://python-poetry.org/docs/#installation), установите его следуя официальной инструкции.
    

3. **Установите зависимости**
    
    ```bash
    poetry install
    ```
    
4. **Настройте переменные окружения**
    
    Создайте файл `.env` в корне проекта и добавьте в него валидные данные, как показано в примере `.env.example`
    
5. **Запустите бота**
    
    ```bash
    poetry run python src/bot.py
    ```
    

## template features to-do list

- [x] Поддержка передачи параметра в `/start` с сохранением его в БД (referral code)
- [x] Пользовательское соглашение, без принятия которого невозможно продолжить работу
- [ ] Интерфейс администратора
    - [ ] Просмотр статистики
    - [ ] Рекламная рассылка
    - [ ] Добавление другого администратора
    - [ ] Бан пользователя
     
## technical features to-do list

- [ ] docker-compose + dockefile
- [ ] alembic migrations
