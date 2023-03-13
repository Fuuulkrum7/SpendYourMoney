## First of all, you need to create a user in your database.
For making it, run mysql, enter your root password and then execute this commands:

```
CREATE USER 'TinkoffUser'@'localhost' IDENTIFIED BY '1nVestm$nt';
```

```
GRANT ALL PRIVILEGES ON *.* TO 'TinkoffUser'@'localhost';
```

Now, you need to run __main.py__ using command line. As it is a pre-version and there's no GUI, all information you can
get would be written in console. Also, venv is not created yet, so we added to __main.py__ a script, which 
downloads all modules, that are necessary for program stable work. 

After this steps, you will see some information about loaded from internet or local database securities. Information, 
using which we are creating request is located near 40-54 lines of code in __main.py__.

#### GetSecurity
So, if you want to find security 
by _figi_, you need to write its name in field __figi=__. Other parts of your response should be written in such way. 
__ticker__=_ticker_, etc. Field __id__ is not necessary to be changed.

Here is an example of such request:

```
s = GetSecurity(
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
    lambda x: print("done, status: ", x),
    TOKEN
)
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

## Первым делом вам нужно создать пользователя в вашей базе данных.
Для этого запустите mysql, введите пароль root и выполните следующие команды:

```
CREATE USER 'TinkoffUser'@'localhost' IDENTIFIED BY '1nVestm$nt';
```

```
GRANT ALL PRIVILEGES ON *.* TO 'TinkoffUser'@'localhost';
```

Теперь вам нужно запустить __main.py__ с помощью командной строки. Поскольку это предварительная версия и в ней нет графического интерфейса, вся информация, которую вы можете получить, будет отображаться в консоли. Также venv еще не создан, поэтому мы добавили в __main.py__ скрипт, который
загружает все модули, необходимые для стабильной работы программы.

После выполнения этих шагов вы увидите некоторую информацию о ценных бумагах, загруженных из Интернета или локальной базы данных. Данные,
с помощью которых мы создаем запрос, находятся в районе 40-54 строк кода в __main.py__. 

#### GetSecurity

Если вы хотите найти ценную бумагу по
_figi_, вам нужно написать ее _figi_ в поле __figi=__. Остальные части вашего ответа должны быть написаны таким же образом.
__ticker__=_ticker_ и т.д. В поле __id__ ничего вносить не нужно.

Вот пример запроса:

```
s = GetSecurity(
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
    lambda x: print("done, status: ", x),
    TOKEN
)
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
