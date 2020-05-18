# Easy-Locust

## Locust Links

* Website: <a href="https://locust.io">locust.io</a>
* Documentation: <a href="https://docs.locust.io">docs.locust.io</a>
* Support/Questions: [Slack signup](https://slack.locust.io/)

## Description

Easy-Locust is an extension tool for Locust. With this tool, you don't need to write locust scripts. What you need to do is just to edit Excel. Easy-Locust will generate locustfile automatically and run it.

If you need master-slave mode, you just need to fill Excel Sheet 'Slave', and use --master. The only precondition is to install the same version locustio in each Slave.
Easy-Locust is not necessary for slaves. 

`easy-locust --web --web-port=8899` -- Run in web mode, you can config and trigger slave-nodes with this mode.

Use `easy-locust --demo` to generate an Excel demo, fill it and start your test.

Same parameters with locust, so I just introduce the different parameters here:

`easy-locust -f xxx.xls` -- This will transform Excel to locustfile, and run it. You can also use `-f xxx.py`.

`easy-locust --xf xxx.xls` -- -- This just transform Excel to locustfile, will not start test.

`easy-locust -f xxx.xls --master -d` -- `-d` is distributed mode, can automatically run slaves. There is one precondition, 
you need write slaves information in Excel at Slave Sheet.

`easy-locust -f xxx.xls --master -d --boomer` -- `--boomer` running boomer client in slaves, which is compiling by Golang. 
In this mode expect_code and expect_str is inoperative. Please keep port 9999 is unused in each slave, when using this mode.

OR, use:
```python
import easy_locust

data = {
    "config": {},
    "apis": [],
    "auth": {},
    "user_info": [],
    "master_ip": "",
    "slaves": []
}

locustfile_str = easy_locust.factory(data)
```

## Bug reporting

Open a Github issue and follow the template listed there.

https://github.com/GuoTengda1993/easy-locust

## Authors

- Guo Tengda

## License

Open source licensed under the MIT license (see _LICENSE_ file for details).


### Change Log
- 0.2.1: Easy-locust web mode.
- 0.1.12: `content-type` support.
- 0.1.11: Add boomer client as slave, which has much more preformance.
- 0.1.10: Delete useless code.
- 0.1.9: Support Json to locustfile. And can use `easy_locust.factory(dict)` to get strings of locustfile. 
- 0.1.6: Optimize locustFileFactory.py
- 0.1.5: Check Response info (status code & expect str) if set "Expect Status Code" in Excel, otherwise not. Rely on locustio>=0.13.5
