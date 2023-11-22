# cxmcli
## Setup
Предполагается что у вас установлен какой либо дистрибутив conda/mamba
```bash
conda install -y -c conda-forge pythonocc-core
python -m pip install ifcopenshell git+https://github.com/contextmachine/mmcore.git multiprocess python-dotenv

```
Также создайте `.env` с необходимыми переменными для подключения:
```dotenv
VIEWER_GRAPHQL_BACKEND_URL=...
VIEWER_USER_ID=...
# Следующая переменная должна быть ввиде json, например '{"x-myheader": "key"}'
VIEWER_GRAPHQL_BACKEND_HEADERS='{}'
```

## Basic usage
Команда ниже возьмет ifc файл и заново перезапишет весь экспорт


```bash
python ifcexport.py "examples/ifc/w7.ifc" \
                    --name "export/w7"
```

Команда ниже загрузит модель в облако как новую.
Если имя заданное в --viewer-name уже существует, возникнет ошибка.

```bash
python uploader.py "export/w7/w7_joined_all.json" \
                    --viewer-name w7-example \
                    --create
```

## Updating practices

Команда ниже возьмет ifc файл и заново перезапишет весь экспорт
```Bash
python ifcexport.py "examples/ifc/w7.ifc" \
                    --name "export/w7" 
```

Команда ниже возьмет ifc файл `./examples/ifc/w7.ifc` и запишет только те модели которые уже есть в `"./export/w7`
Это нужно чтобы можно было удалить файлы ненужных слоев один раз, а после получать всегда чистую модель.
```Bash  
python ifcexport.py "examples/ifc/w7.ifc" \
                    --name "export/w7" \
                    --use-last
``` 

Следующую команду нужно вызвать после любой из предыдущих. Для того чтобы загрузить геометрию во вьювер.
Вы также можете поместить модель в конкретные сцены добавив дополнительные аргументы.
Для этого смотрите файл `"add_to_scene.sh"`
```Bash
python uploader.py "export/w7/w7_joined_all.json" \
                    --viewer-name w7-example \
                    --update 
```
При режиме `--update` вместо `--viewer-name` можно передать `--viewer-id`
Это не может работать в режиме `--create`, тк id еще не создан.
```Bash
python uploader.py "export/w7/w7_joined_all.json" \
                    --viewer-id 93 \
                    --update
```

## Attach to scenes            
В этом примере не используется не один из флагов: `--create`,`--update`.
Это означает что модель никуда загружаться не будет, а первый аргумент пути будет проигнорирован.
Это может быть полезно если не нужно обновлять саму геометрию,
а допустим, хочется единовременно добавить модель в кучу разных сцен.
В этом случае просто передайте сколько угодно сцен по принципу `--scene <scene name>` как показано ниже.
```Bash
python uploader.py "export/w7/w7_joined_all.json" \
                    --viewer-name w7-example \
                    --scene "MFB MM Test" \
                    --scene "My W7 example" \
                    --title "W7"
```
