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

Open project folder in terminal and create venv
```commandline
python -m venv /path/to/project/venv
```

Then you should activate venv. Run this command if you are using Linux or
macOS
```commandline
source /path/to/project/venv/bin/activate
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
In the bottom left corner if wain window is located "Settings" button. Click
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
Remember that neural network in case of white text cn make mistakes to, it is not recommendation

# Developer documentation

### SecurityInfo
This class has 5 fields - __id__, __figi__, __ticker__, __security_name__, __class_code__,
or main info about security. This class is used for securities search. 

## API requests

### GetSecurity
So, if you want to find security using backend
by _figi_, you need to write its name in field __figi=__. Other parts of your response should be written in such way. 
__ticker__=_ticker_, etc. Field __id__ is not necessary to be changed.

Here is an example of such request:

```
security_thread = GetSecurity(
    StandardQuery(
        SecurityInfo(
            id=0,
            figi="TCS009029557",
            security_name="",
            ticker="SBERP",
            class_code="SMAL"
        ),
        ""
    ),
    lambda x: print("done, status: ", x[0]),
    TOKEN
)
security_thread.start()
```

As you can see, it is permitted not to fill each field, it is allowed to fill only that variables, that you 
know.


If you want to find as much, as it is possible, pay attention for second variable in __StandardQuery__ constructor.
In this line you can write all information about security, for which there's no field in __SecurityInfo__ (for example, 
for _isin_). But be careful! It can take lots of time, if you would try to find information about lots of papers, like 
`security_name = " "` without writing other information about security, request would take lots of time, because this class 
is created for looking not big number of papers (or for looking big number of them locally. But api-request will take too much time)


#### LoadAllSecurities
If you want this program to work faster, just use first class `LoadAllSecurities`
This class must be used only one time (or each time after clearing database). This class
downloads __all__ securities from API. Of course, it's impossible to load all data about dividends and
coupons in one time, so this class loads only Bonds and Stocks. For downloading just write 

```
loader = LoadAllSecurities(
    lambda x: print(f"done, code = {x}"),
    TOKEN
)
loader.start()
```
It will take near 8-12 seconds (depends on your Internet speed)

#### GetSecurityHistory

If you need to load historic candles of security, you can use class GetSecurityHistory.
For correct work, you should use first GUI for getting __figi__ of security. Then
you should create object of SecurityInfo

```
info = SecurityInfo(
    id=0,
    figi=figi,
    security_name="",
    ticker="",
    class_code=""
)
```

Then you should run such class object

```
history = GetSecurityHistory(
    info=info,
    _from=now() - timedelta(days=300),
    to=now(),
    interval=CandleInterval.CANDLE_INTERVAL_DAY,
    token=TOKEN,
    on_finish=lambda data: print(
        *data[1],
        sep='\n'
    )
)
history.start()
```

As you can seem this class loads historic candles for 300 days as one day candles.

## Первым делом вам нужно создать пользователя в вашей базе данных.
Для этого запустите mysql, введите пароль root и выполните следующие команды:

```
CREATE USER 'TinkoffUser'@'localhost' IDENTIFIED BY '1nVestm$nt';
```

```
GRANT ALL PRIVILEGES ON *.* TO 'TinkoffUser'@'localhost';
```

Откройте терминал в папке, где находятся файлы проекта и выполните следующую команду:

```commandline
pip install -r requirements.txt
```

После этого запустите __main.py__ из терминала. 

```commandline
python main.py
```

Поскольку это предварительная версия и графический интерфейс находтся в стадии альфа-версии, вся информация, 
которую вы можете получить, будет отображаться в консоли.

### Use GUI for search

В открывшемся окне нажмите "go to registration" и введите логин, пароль и
токен tinkoff для создания нового пользователя в бд. После успешной регистрации или авторизации
(при следующем запуске) вы сможете использовать доступный на данный момент функционал -
поиск ценных бумаг. Используя поиск, вы сможете получить список JSON-форматированных данных о ценных бумагах по ключевым словам. Это ключевое слово может быть именем
компании, figi, ticker или class-code. Например, вы можете написать тикер "LKOH", чтобы увидеть информацию о ценных бумагах "Лукойл".
Нажав "Load all" вы значительно увеличите скорость поиска ценных бумаг. Данное действие рекомендуется
сделать в первую очередь при начале работы с приложением.

#### GetSecurity

Если вы хотите найти ценную бумагу по
_figi_, вам нужно написать ее _figi_ в поле __figi=__. Остальные части вашего ответа должны быть написаны таким же образом.
__ticker__=_ticker_ и т.д. В поле __id__ ничего вносить не нужно.

Вот пример запроса:

```
security_thread = GetSecurity(
    StandardQuery(
        SecurityInfo(
            id=0,
            figi="TCS009029557",
            security_name="",
            ticker="SBERP",
            class_code="SMAL"
        ),
        ""
    ),
    lambda x: print("done, status: ", x[0]),
    TOKEN
)
security_thread.start()
```

Как видно из данного примера, можно не заполнять каждое поле класса, а только те, данные для которых вы знаете.

Если вы хотите загрузить как можно больше ценных бумаг, обратите внимание на вторую переменную в конструкторе __StandardQuery__.
В этой строке вы можете написать всю информацию о безопасности, для которой нет поля в __SecurityInfo__ (например,
для _isin_). Но будьте осторожны! Это может занять много времени, если вы попытаетесь найти информацию о большом количестве ценных бумаг, указывая, к примеру, `security_name = " "` без указания другой информации о цб, запрос займет много времени, потому что этот класс
создан для поиска небольшого количества бумаг (или для поиска большого количества, но локально. Сам же api-запрос будет занимать слишком много времени)

#### LoadAllSecurities
Если вы хотите ускорить работу программы, попробуйте воспользоваться предварительной 
загрузкой всех ценных бумаг, которую осуществляет класс `LoadAllSecurities`. 
Этот класс должен быть запущен только один раз (или каждый раз после пересоздания бд). 
Разумеется, загрузка всех данных, заняла бы слишком много времени, поэтому данный класс
загружает только Акции и Облигации (Stocks и Bonds). Для загрузки используйте данный код:
```
loader = LoadAllSecurities(
    lambda x: print(f"done, code = {x}"),
    TOKEN
)
loader.start()
```
Загрузка займет около 8-12 секунд, время зависит от скорости интернета и памяти.

#### GetSecurityHistory

Если вам нужно загрузить историю курса ценной бумаги, вы можете использовать класс GetSecurityHistory.
Для корректной работы следует сначала использовать GUI для получения __figi__ ценной бумаги. Затем
вы должны создать экземпляр SecurityInfo

```
info = SecurityInfo(
    id=0,
    figi=figi,
    security_name="",
    ticker="",
    class_code=""
)
```

И запустить данный код

```
history = GetSecurityHistory(
    info=info,
    _from=now() - timedelta(days=300),
    to=now(),
    interval=CandleInterval.CANDLE_INTERVAL_DAY,
    token=TOKEN,
    on_finish=lambda data: print(
        *data[1],
        sep='\n'
    )
)
history.start()
```

Как можно заметить, данный класс загружает и выводит историю курса цб за 300 дней по дням.
