# Содержание


1. [Developer documentation](#developer-documentation)
   1. [Securities classes](#securities-classes)
      1. [SecurityInfo](#securityinfo)
      2. [Security](#security)
   2. [API requests](#api-requests)
      1. [GetSecurity](#getsecurity)
      2. [GetCoupons, GetDividends](#getcoupons-getdividends)
      3. [LoadAllSecurities](#loadallsecurities)
      4. [GetSecurityHistory](#getsecurityhistory)
      5. [SubscribeOnMarket](#subscribeonmarket)
   3. [Predictions](#predictions)
      1. [Bollinger](#bollinger)
      2. [RSI](#rsi)
2. [Документация разработчика](#документация-разработчика)
   1. [Классы ценных бумаг](#классы-ценных-бумаг)
      1. [SecurityInfo](#securityinfo-1)
      2. [Security](#security-1)
   2. [API запросы](#api-запросы)
      1. [GetSecurity](#getsecurity-1)
      2. [GetCoupons, GetDividends](#getcoupons-getdividends-1)
      3. [LoadAllSecurities](#loadallsecurities-1)
      4. [GetSecurityHistory](#getsecurityhistory-1)
      5. [SubscribeOnMarket](#subscribeonmarket-1)
   3. [Предсказания](#предсказания)
      1. [Bollinger](#bollinger-1)
      2. [RSI](#rsi-1)

# Developer documentation
## Securities classes
### SecurityInfo
This class has 5 fields – **id**, **figi**, **ticker**, **security_name**, **class_code**,
or main info about security. This class is used for securities search.
Example:

```
info = SecurityInfo(
    id=0,
    figi="TCS009029557",
    security_name="Сбер Банк Привилегированные акции",
    ticker="SBERP", 
    class_code="SMAL"
)
```

### Security
This class contains full info about security, which is not connected with 
security type. Contains instance of SecurityInfo, lot size (lot), currency, 
contry, where business is located and country code (UK, RU etc), 
sector of economy and security type, stock or bond.

```
security = Security(
    class_code=loaded_instrument.class_code,
    id=0,
    figi="BBG004730N88",
    ticker="SBER",
    security_name="Сбер Банк",
    lot=10,
    currency="rub",
    country="Российская Федерация",
    country_code="RU",
    sector="FINANCIAL",
    security_type=SecurityType.STOCK
)
```

Other classes (Dividends, Coupons) and Securities children (Stock, Bond) you can find in XMI file named securities.xmi .


## API requests

All api requests classes extends Qthread, soSecurities classes. Some of them 
extends abstract class SecurityGetter. Each class need function reference as 
argument on_finish. This function will be called, when thread need to send 
result of its work. It will send tuple of two values — int status code, 
where 200 is ok, and result of its work. Also each class needs tinkoff token

### GetSecurity

So, if you want to find security using backend by figi, you need to write its name in field figi=. Other parts of your response should be written in such way: ticker=your_ticker, etc. Field id is not necessary to be changed. Class sends in function (in example its a lambda-function) tuple with status code and list of found securities. 

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
know. Class extends  SecurityGetter.
Other arguments (all they are key arguments):

    • insert_to_db — bool, used if you don’t need to save security locally
    • load_full_info — bool, if it is True, you would get list of Bonds and Stocks, if it is False, you would get list of Securities
    • check_locally, check_only_localy — use database for seacrh, use only database.
    • load_dividends, load_coupons — if true, coupons and divedends would be downloaded

If you want to find as much, as it is possible, pay attention for second variable 
in StandardQuery constructor. In this line you can write all information 
about security, for which there's no field in SecurityInfo (for example,  
for isin). But be careful! It can take lots of time, if you would try 
to find information about lots of papers, using name like  security_name = " " 
without writing other information about security, request would take lots of 
time, because this class 

is created for looking not big number of papers (or for looking big number 
of them locally. But api-request will take too much time)

### GetCoupons, GetDividends
Both works same as previous class and has same arguments 
(without load_dividends, load_coupons). Example:


```query = StandardQuery(
    SecurityInfo(
        ticker="SBER",
    ),
    ""
)
```
```
coup = GetCoupons(
    query,
    lambda x: print(x),
    TOKEN
)
coup.start()
```
```
div = GetDividends(
    query,
    lambda x: print(x),
    TOKEN
)
div.start()
```

### LoadAllSecurities
If you want this program to work faster, just use first class 
LoadAllSecurities This class must be used only one time (or each
time after clearing database). This class downloads all securities from 
API. Of course, it's impossible to load all data about dividends and 
coupons in one time, so this class loads only Bonds and Stocks. 
For downloading just write 

```
loader = LoadAllSecurities(
    lambda x: print(f"done, code = {x[0]}"),
    TOKEN
)
loader.start()
```

It will take near 8-12 seconds (depends on your Internet speed)

### GetSecurityHistory
Extends Qthread.
If you need to load historic candles of security, you can use class 
GetSecurityHistory. For correct work, you should use first GUI for 
getting figi of security. Then you should create object of SecurityInfo

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

As you can see, this class loads historic candles for 300 days as one day candles.
Arguments:

    • info — secutity info
    • _from — start date
    • to — end date
    • inerval — instance of CandleInterval, its a enum from tinkoff investments api
    • token — user token
    • on_finish — function reference


### SubscribeOnMarket
Using this this class you can create subscription thread, which 
would send you one SecurityHistory candle. Example:

```
self.subscribe_thread = SubscribeOnMarket(
    info,
    TOKEN,
    lambda x: print(*x)
)
self.subscribe_thread.start()
```

Arguments:

    • fisrt is SecurityInfo
    • second is token
    • thrid is function reference
    • interval — candle interval, three ore one minutes, default one. Is instance of enum SubscriptionInterval
    • subscription — subscription action, SUBSCRIPTION_ACTION_SUBSCRIBE or SUBSCRIPTION_ACTION_UNSUBSCRIBE. Instance of enum SubscriptionAction.

## Predictions

### Bollinger

To call the class, you need to create a thread variable and assign it the 
Bollinger class prototype with parameters:

    • start_date: datetime. Start date of the prediction in datetime format 
    • info: SecurityInfo. Information about a security, specified as the SecurityInfo data class
    • token Token for accessing TinkofAPI
    • end_date: datetime. End date of forecast in datetime format
    • on_finish - The function to which the results of class execution are passed
    • period: int. The period for which to calculate the moving average
    • set_standard_fl: float. Upper and Lower Bollinger Band Rejection Multiplier  
    • candle_interval: CandleInterval. Candle time interval in CandleInterval format

An example of a class call:

```
self.bollinger_thread = Bollinger(    
    start_date, 
    info,
    token,
    end_date,
    on_finish,
    period,
    set_standard_fl,
    candle_interval
)
self.bollinger_thread.start()
```

An example of a function to which data is passed:

```
def on_finish(self, result): 
    code, data = result
```

data - the data passed from the data class
data is a matrix consisting of three rows, which stores the calculated data:

    • The first row is an array of upper Bollinger band values
    • The second row is an array of Bollinger Middle Band values.

### RSI
To call the class, you need to create a thread variable and assign 
it the prototype of the RSI class with parameters:

    • num_candl: int. The number of candles that are calculated from the start date
    • token. Token for accessing TinkofAPI
    • start_date: datetime. Start date of the forecast in datetime format 
    • end_date: . End date of forecast in datetime format
    • info: SecurityInfo. Information about a security, specified as the SecurityInfo data class
    • on_finish, The function to which the results of class execution are passed
    • rsi_step: int. Interval for which RSI is calculated
    • candle_interval: CandleInterval. Candle time interval in CandleInterval format

An example of a class call:

```
self.rsi_thread = RSI(
    num_candl,
    token,
    start_date, 
    end_date,
    info,
    on_finish, 
    rsi_step, 
    candle_interval
)
self.rsi_thread.start()
```

An example of a function to which data is passed:

```
def on_finish(self, result): 
    code, data = result
```

data - the data passed from the data class

data is an array of calculated data values

# Документация разработчика
## Классы ценных бумаг
### SecurityInfo
Этот класс имеет 5 полей – **id**, **figi**, **ticker**, **security_name**, **class_code**, 
или же главную информацию о ценной бумаге. Этот класс используется для поиска ценных бумаг.
Пример:

```
info = SecurityInfo(
    id=0,
    figi="TCS009029557",
    security_name="Сбер Банк Привилегированные акции",
    ticker="SBERP", 
    class_code="SMAL"
)
```

### Security
Этот класс содержит полную информацию о ценной бумаге, 
которая не связана с типом цб (акция или же облигация). Содержит экземпляр 
`SecurityInfo`, размер лота (lot), валюту, страну, где расположен 
бизнес и код страны (UK, RU и т.д.), сектор экономики и тип ценной бумаги, 
`SecurityType.STOCK` или `SecurityType.BOND`.

Пример:

```
security = Security(
    class_code=loaded_instrument.class_code,
    id=0,
    figi="BBG004730N88",
    ticker="SBER",
    security_name="Сбер Банк",
    lot=10,
    currency="rub",
    country="Российская Федерация",
    country_code="RU",
    sector="FINANCIAL",
    security_type=SecurityType.STOCK
)
```

Другие классы (дивиденды, купоны) и наследников класса `Security` (`Bond`, `Stock`)
более полно описаны в файле XMI с названием securities.xmi.
## API запросы

Все классы запросов api наследуются от класса `Qthread`. Некоторые из них 
наследуют абстрактный класс SecurityGetter. Каждому классу нужна ссылка на 
функцию в качестве аргумента on_finish. Эта функция будет вызвана, когда 
потоку потребуется отправить результат своей работы. Он отправит кортеж из двух 
значений — код состояния int, где 200 — все хорошо, и результат своей работы. 
Также каждому классу нужен токен tinkoff.

### GetSecurity

Итак, если вы хотите найти ценную бумагу по **figi**, вам нужно написать ее фиги в поле figi=. Другие части вашего ответа должны быть написаны таким образом: ticker=your_ticker и т.д. id изменять не обязательно. Класс отправляет в функцию (в примере это лямбда-функция) кортеж с кодом состояния и списком найденных ценных бумаг. 

Вот пример такого запроса:

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

Как вы можете видеть, можно не заполнять каждое поле, разрешено заполнять только те переменные, которые вам известны. Класс наследует  SecurityGetter.
Другие аргументы (все они являются ключевыми аргументами):

    • insert_to_db — bool, используется, если вам не нужно сохранять цб локально
    • load_full_info — bool, если это правда, вы получите список облигаций и акций, если это ложь, вы получите список ценных бумаг
    • check_locally, check_only_localy — надо ли использовать базу данных для поиска, надо ли использовать только базу данных.
    • load_dividends, load_coupons — если истина, то будут загружены купоны и дивиденды

Если вы хотите найти как можно больше цб, обратите внимание на вторую переменную в стандартном конструкторе запросов. В этой строке вы можете записать всю информацию о цб, для которой нет поля в SecurityInfo (например, для isin). Внимание! Если вы попытаетесь найти информацию о множестве цб, это может занять много времени, если использовать, к примеру, имя цб security_name = " " без записи другой информации о цб, запрос займет много времени, потому что этот класс создан для просмотра небольшого количества ценных бумаг (или для поиска большого их количества локально. Запрос же через api займет слишком много времени)

### GetCoupons, GetDividends

Оба работают так же, как и предыдущий класс, и имеют те же аргументы 
(без load_dividends, load_coupons). Пример:

```
query = StandardQuery(
    SecurityInfo(
        ticker="SBER",
    ),
    ""
)
```
```
coup = GetCoupons(
    query,
    lambda x: print(x),
    TOKEN
)
coup.start()
```
```
div = GetDividends(
    query,
    lambda x: print(x),
    TOKEN
)
div.start()
```

## LoadAllSecurities
Если вы хотите, чтобы эта программа работала быстрее, просто используйте класс 
`LoadAllSecurities`, он должен использоваться только один раз (или каждый раз 
после очистки базы данных). Этот класс загружает все ценные бумаги через API 
и сохраняет их локально. Конечно, невозможно загрузить все данные о дивидендах 
и купонах за один раз, поэтому этот класс загружает только облигации и акции. 
Для скачивания просто напишите

```
loader = LoadAllSecurities(
    lambda x: print(f"done, code = {x[0]}"),
    TOKEN
)
loader.start()
```

Займет около 8-12 секунд (зависит от скорости вашего интернета)

### GetSecurityHistory
Наследует `Qthread`.
Если вам нужно загрузить курс цб, вы можете использовать класс 
`GetSecurityHistory`. Для корректной работы вам стоит использовать 
графический интерфейс для отображения информации о цб в виде графика. 
Сначала вы должны создать экземпляр `SecurityInfo`

```
info = SecurityInfo(
    id=0,
    figi=figi,
    security_name="",
    ticker="",
    class_code=""
)
```

Затем вы должны создать поток и запустить его:

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

Как вы можете видеть, этот класс загружает свечи (однодневные) за 300 дней.
Аргументы:

    • info — secutity info
    • _from — начальная дата
    • to — конечная дата
    • inerval — экземпляр CandleInterval, это нумератор из tinkoff investments api
    • token — токен
    • on_finish — ссылка на функцию


### SubscribeOnMarket

Используя этот класс, вы можете создать поток подписки, который отправляет 
вам одну свечу SecurityHistory каждую минуту (или три, зависит от типа свечи, 
выбранного при создании). Пример:

```
self.subscribe_thread = SubscribeOnMarket(
    info,
    TOKEN,
    lambda x: print(*x)
)
self.subscribe_thread.start()
```

Аргументы:

    • первый - SecurityInfo
    • второй - токен
    • третий — ссылка на функцию
    • interval — интервал между свечами. По умолчанию одна минута, можно указать три минуты. Экземпляр нумератора SubscriptionInterval
    • subscription — действие с подпиской, SUBSCRIPTION_ACTION_SUBSCRIBE или SUBSCRIPTION_ACTION_UNSUBSCRIBE. Экземпляр  нумератора SubscriptionAction.

## Предсказания

### Bollinger

Для вызова класса требуется создать переменную потока и присвоить ей 
прототип класса Bollinger с параметрами:

    • start_date: datetime. Дата начала прогноза в формате datetime 
    • info: SecurityInfo. Информация о ценной бумаге в виде класса данных SecurityInfo
    • token. Токен для обращения к TinkofAPI
    • end_date: datetime. Дата конца прогноза в формате datetime
    • on_finish. Функция, в которую передаются результаты выполнения класса
    • period: int. Период, за который считать среднюю скользящую
    • set_standard_fl: float. Множитель отклонения верхней и нижней линии Боллинджера  
    • candle_interval: CandleInterval. Временной интервал свечи в формате CandleInterval
Пример вызова класса:

```
self.bollinger_thread = Bollinger(    
    start_date, 
    info,
    token,
    end_date,
    on_finish,
    period,
    set_standard_fl,
    candle_interval
)
self.bollinger_thread.start()
```

Пример функции, в которую передаются данные:

```
def on_finish(self, result): 
    code, data = result
```

data - данные переданные из класса данные
data представляет собой матрицу, состоящую из трёх рядов, в которой 
хранятся просчитанные данные:

    • Первый ряд, это массив значений верхней линии Боллинджера
    • Второй ряд, это массив значений средней линии Боллинджера
    • Третий ряд, это массив значений нижней линии Боллинджера

### RSI

Для вызова класса требуется создать переменную потока и присвоить 
ей прототип класса RSI с параметрами:

    • num_candl: int. Количество свечей, которые просчитываются от даты начала
    • token. Токен для обращения к TinkofAPI
    • start_date: datetime. Дата начала прогноза в формате datetime 
    • end_date: datetime. Дата конца прогноза в формате datetime
    • info: SecurityInfo. Информация о ценной бумаге в виде класса данных SecurityInfo
    • on_finish, Функция, в которую передаются результаты выполнения класса
    • rsi_step: int. Интервал, за который считается RSI
    • candle_interval: CandleInterval. Временной интервал свечи в формате CandleInterval

Пример вызова класса:

```
self.rsi_thread = RSI(
    num_candl,
    token,
    start_date, 
    end_date,
    info,
    on_finish, 
    rsi_step, 
    candle_interval
)
self.rsi_thread.start()
```

Пример функции, в которую передаются данные:

```
def on_finish(self, result): 
    code, data = result
```

data - данные переданные из класса данные

data представляет собой массив значений просчитанных данных