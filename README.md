### First of all, you need to create a user in your database.
For making it, run mysql, enter your root password and then execute this commands:

`CREATE USER 'TinkoffUser'@'localhost' IDENTIFIED BY '1nVestm$nt';`

`GRANT ALL PRIVILEGES ON *.* TO 'TinkoffUser'@'localhost';`

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
know. __WARNING__. If now only name of "security", program will always try to find it in internet, because at this moment
we have some problems with python, which interprets some strings with `f"LIKE %{name}%"`. We'll fix this problem soon.

If you want to find as much, as it is possible, pay attention for second variable in __StandardQuery__ constructor.
In this line you can write all information about security, for which there's no field in __SecurityInfo__ (for example, 
for _isin_). But be careful! It can take lots of time, if you would try to find information about lots of papers, like 
`security_name = " "` without writing other information about security, request would take lots of time, because this class 
is created for looking not big number of papers (or for looking big number of them locally. But api-request will take too much time)
