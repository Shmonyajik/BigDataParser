# BigDataParser
## Запуск проекта:
+ Установить и запустить [docker](https://www.docker.com/products/docker-desktop)
+ Скачать код из этого репозитория
+ (Optional) поменять параметры в url к api
![image](https://github.com/Shmonyajik/BigDataParser/assets/83132326/7fa06203-e76c-44d9-9d65-f8c6c2ae9905)
Конструктор тут: https://docs.reservoir.tools/reference/gettokensv6
+ **Запускать на Linux**
+ Запустить скрипт `bash scripts/setup.sh`
+ После выполнения всех операций следует остановить и удалить контейнеры с помощью команды `bash scripts/clear.sh`
---
Для локального тестирования скрипта необходимо установить необходимые пакеты командой `pip install -r requirements.txt`, а затем запустить сам скрипт командой `py core/main.py`

**Error** `max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]`
1. `sudo nano /etc/sysctl.conf`
2. insert `vm.max_map_count=262144`
3. `sudo sysctl -p`
