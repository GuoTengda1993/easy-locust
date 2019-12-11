# Easy-Locust

## Locust Links

* Website: <a href="https://locust.io">locust.io</a>
* Documentation: <a href="https://docs.locust.io">docs.locust.io</a>
* Support/Questions: [Slack signup](https://slack.locust.io/)

## Description

Easy-Locust is an extension tool for Locust. With this tool, you don't need to write locust scripts. What you need to do is just to edit Excel. Easy-Locust will generate locustfile automatically and run it.

If you need master-slave mode, you just need to fill Excel Sheet 'Slave', and use --master. The only precondition is to install the same version locustio in each Slave.
Easy-Locust is not necessary for slaves. 

Use `easy-locust --demo` to generate an Excel demo, fill it and start your test.

Same parameters with locust, so I just introduce the different parameters here:

`easy-locust -f xxx.xls` -- This will transform Excel to locustfile, and run it. You can also use `-f xxx.py`.

`easy-locust --xf xxx.xls` -- -- This just transform Excel to locustfile, will not start test.

`easy-locust -f xxx.xls --master -d` -- `-d` is distributed mode, can automatically run slaves. There is one precondition, you need write slaves information in Excel at Slave Sheet.


## Bug reporting

Open a Github issue and follow the template listed there.

https://github.com/GuoTengda1993/easy-locust

## Authors

- Guo Tengda

## License

Open source licensed under the MIT license (see _LICENSE_ file for details).

