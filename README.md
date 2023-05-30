# User documentation

## First steps
Firstly you need to crete user for MySQL database.
Run mysql, enter your root password and then execute this commands:

```
CREATE USER 'TinkoffUser'@'localhost' IDENTIFIED BY '1nVestm$nt';
```

```
GRANT ALL PRIVILEGES ON *.* TO 'TinkoffUser'@'localhost';
```

Now you need to create folder for project. After creating it, open terminal execute this command:
```commandline
cd full/path/to/project/
```

Clone repository
```commandline
git clone -b release --single-branch https://github.com/Fuuulkrum7/SpendYourMoney.git .
```

Now you should create venv:
```commandline
python -m venv venv
```

Then you should activate venv. Run this command if you are using Linux or
macOS
```commandline
source venv/bin/activate
```

If you are using Windows, run
```commandline
.\venv\Scripts\activate
```

These commands should be run each time, when you want to use this app


Then execute this to install necessary modules
```commandline
pip install -r requirements.txt
```

Now you need to run __main.py__ using command line. 

```commandline
python main.py
```

When work with this app would be ended, run this command
```commandline
deactivate
```

## Main window

### How to use search
In opened window click "go to registration" and then enter login, password and 
tinkoff token to create new user in db. After successful registration or login 
(next launch) you will be able to use the currently available functionality - 
security search and download. Using search, you will be able to get list of 
different securities you were looking for. Keywords for this search can be: name of
company, figi, ticker or class-code. For example, you can write ticker "LKOH" 
and press search button named "Find Security" to see information on "Лукойл" securities.
By clicking "Load all" you will significantly increase the speed of securities 
search. You should press it, when you run this program for first time or if you
want to update local database (but don't run it very often).

Also, you can use advanced search. This method is useful, for example, 
if security has part of ticker in its name. It should be mentioned, that some
Stocks and Bonds has same tickers, and in such cases advanced search is very useful too.
If you want to use it, just press button "Advanced search". Four text fields named
__figi__, __security name__, __ticker__ and __class code__. Standard text field would
be disabled. Remember that search runs with button "Find Security" too.

### Settings
In main window "Settings" button is located in the left bottom corner. Click
it to open window "Settings". In this window are located theme modes (dark mode and light mode)
and fonts list. If you want to add your font, open folder info/files/fonts and 
copy your font file in this folder.


## Security window
As you remember, you can get list of securities using search. You can click on any of 
these securities and this click will open a window with three tabs in it.

### Main info tab
In this tab you can find information about this security - country, where company is located,
issue size and a lot of other information. 

### Subdata tab
In this tab are located coupons or dividends (depends on type of security).
You click on them, but nothing would happen

### Course tab
In this tab you can find plot, that shows security course using candles, type of which
can be chosen in list of different time candles - 1 minute, 5 minute, 1 hour e.t.c.
Near this list you can find two checkboxes - RSI and Bollinger. Using them you
can get rsi plot and draw (automatically) bollinger lines.

In the left upper corner you can find result of prediction, made by neural network.
If result is colored red - chance of mistake is really high. In case of cyan color chance is a bit lower.
Remember that neural network in case of normal text can make mistakes too, this is not a recommendation.

# Документация пользователя

## Первые шаги
Во-первых, вам нужно создать пользователя для базы данных MySQL.
Запустите mysql, введите свой пароль root, а затем выполните следующие команды:

```
CREATE USER 'TinkoffUser'@'localhost' IDENTIFIED BY '1nVestm$nt';
```

```
GRANT ALL PRIVILEGES ON *.* TO 'TinkoffUser'@'localhost';
```

Теперь вам нужно создать папку для проекта. После ее создания откройте терминал и выполните эту команду:
```commandline
cd full/path/to/project/
```

Скопируйте репозиторий
```commandline
git clone -b release --single-branch https://github.com/Fuuulkrum7/SpendYourMoney.git .
```

Теперь вы должны создать venv:
```commandline
python -m venv venv
```

Затем вы должны активировать venv. Запустите эту команду, если вы используете Linux или
macOS
```commandline
source venv/bin/activate
```

Если вы используете Windows, запустите
```commandline
.\venv\Scripts\activate
```

Эти команды следует запускать каждый раз, когда вы хотите использовать это приложение.


Затем выполните это, чтобы установить необходимые модули
```commandline
pip install -r requirements.txt
```

Теперь вам нужно запустить __main.py__ с помощью командной строки.

```commandline
python main.py
```

Когда работа с этим приложением будет завершена, запустите эту команду
```commandline
deactivate
```

## Главное окно

### Как использовать поиск
В открывшемся окне нажмите "перейти к регистрации", а затем введите логин, пароль и
токен tinkoff, чтобы создать нового пользователя в базе данных. После успешной регистрации или входа в систему
(следующий запуск) вы сможете использовать доступный в настоящее время функционал -
поиск по ценным бумагам и загрузку. Используя поиск, вы сможете получить список
различных ценных бумаг, которые вы искали. Ключевыми словами для этого поиска могут быть: название
компании, figi, тикер или код класса. Например, вы можете ввести тикер "LKOH"
и нажать кнопку поиска с названием "Find security", чтобы просмотреть информацию о ценных бумагах "Лукойл".
Нажав "Load all", вы значительно увеличите скорость поиска ценных бумаг. Вы должны нажать ее, когда запускаете эту программу в первый раз или если вы
хотите обновить локальную базу данных (но запускайте ее не очень часто).

Также вы можете воспользоваться расширенным поиском. Этот метод полезен, например,
если в названии ценной бумаги есть часть тикера. Следует отметить, что некоторые
Акции и облигации имеют одинаковые тикеры, и в таких случаях расширенный поиск тоже очень полезен.
Если вы хотите им воспользоваться, просто нажмите кнопку "Расширенный поиск". Четыре текстовых поля с именами
__figi__, __security name__, __ticker__ и __class code__. Стандартное текстовое поле будет
отключено. Помните, что поиск также выполняется с помощью кнопки "Find security".

### Настройки
В левом нижнем углу главного окна расположена кнопка "Settings". Нажмите
на нее, чтобы открыть окно "Settings". В этом окне расположены темы (темная и светлая тема)
и список шрифтов. Если вы хотите добавить свой шрифт, откройте папку info/files/fonts и
скопируйте файл вашего шрифта в эту папку.


## Окно ценной бумаги
Как вы помните, список ценных бумаг вы можете получить с помощью поиска. Вы можете нажать на любую из
этих ценных бумаг, и этот клик откроет окно с тремя вкладками в нем.

### Главная информационная вкладка
На этой вкладке вы можете найти информацию об этой ценной бумаге - стране, в которой находится компания,
обьем выпуска и много другой информации.

### Вкладка вложенных данных
На этой вкладке расположены купоны или дивиденды (зависит от типа ценной бумаги).
Вы нажимаете на них, но ничего не происходит.

### Вкладка курса
На этой вкладке вы можете найти график, который показывает курс ценной бумаги с использованием свечей, тип которых
можно выбрать из списка свечей с разным временем - 1 минута, 5 минут, 1 час и т.д.
Рядом с этим списком вы можете найти два флажка - RSI и Bollinger. Используя их, вы
можете получить график rsi и нарисовать (автоматически) линии Боллинджера.

В левом верхнем углу вы можете найти результат предсказания, сделанного нейронной сетью.
Если результат окрашен в красный цвет - вероятность ошибки действительно высока. В случае голубого цвета вероятность немного ниже.
Помните, что нейронная сеть в случае обычного текста может допускать ошибки, это не рекомендация.
