### First of all, you need to create a user in your database.
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
using which we are creating request is located near 40-54 lines of code in __main.py__. So, if you want to find security 
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
know. __WARNING__. If name of "security" is specified only, program will always try to find it in internet, because at this moment
we have some problems with python, which interprets some strings with `f"LIKE %{name}%"`. We'll fix this problem soon.

If you want to find as much, as it is possible, pay attention for second variable in __StandardQuery__ constructor.
In this line you can write all information about security, for which there's no field in __SecurityInfo__ (for example, 
for _isin_). But be careful! It can take lots of time, if you would try to find information about lots of papers, like 
`security_name = " "` without writing other information about security, request would take lots of time, because this class 
is created for looking not big number of papers (or for looking big number of them locally. But api-request will take too much time)


### Первым делом вам нужно создать пользователя в вашей базе данных.
Для этого запустите mysql, введите пароль root и выполните следующие команды:

```
CREATE USER 'TinkoffUser'@'localhost' IDENTIFIED BY '1nVestm$nt';
```

```
GRANT ALL PRIVILEGES ON *.* TO 'TinkoffUser'@'localhost';
```

Теперь вам нужно запустить __main.py__ с помощью командной строки. Поскольку это предварительная версия и в ней нет графического интерфейса, вся информация, которую вы можете получить, будет отображаться в консоли. Также venv еще не создан, поэтому мы добавили в __main.py__ скрипт, который
загружает все модули, необходимые для стабильной работы программы.

После выполнения этих шагов вы увидите некоторую информацию о ценных бумагах, загруженных из Интернета или локальной базы данных. Информация,
с помощью которого мы создаем запрос, находится в районе 40-54 строк кода в __main.py__. Так что если вы хотите найти ценную бумагу по
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

Как видите, можно не заполнять каждое поле, можно заполнять только те переменные, которые вы
знать. __ПРЕДУПРЕЖДЕНИЕ__. Если указано только имя ценной бумаги, программа всегда будет пытаться найти ее в интернете, т.к. в этот момент
у нас есть некоторые проблемы с python, который интерпретирует некоторые строки с `f"LIKE %{name}%"`. Мы исправим эту проблему в ближайшее время.

Если вы хотите загрузить как можно больше ценныз бумаг, обратите внимание на вторую переменную в конструкторе __StandardQuery__.
В этой строке вы можете написать всю информацию о безопасности, для которой нет поля в __SecurityInfo__ (например,
для _isin_). Но будьте осторожны! Это может занять много времени, если вы попытаетесь найти информацию о большом количестве ценных бумаг, указывая, к примеру, `security_name = " "` без указания другой информации о цб. Запрос займет много времени, потому что этот класс
создан для поиска небольшого количества бумаг (или для поиска большого количества, но локально. Сам же api-запрос будет занимать слишком много времени)
