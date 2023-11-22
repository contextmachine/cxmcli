# Команда ниже возьмет ifc файл и заново перезапишет весь экспорт
python ifcexport.py "examples/ifc/w7.ifc" \
                    --name "export/w7" \

# Команда ниже загрузит модель в облако как новую.
# Если имя заданное в --viewer-name уже существует, возникнет ошибка.
python uploader.py "export/w7/w7_joined_all.json" \
                    --viewer-name w7-example \
                    --create



