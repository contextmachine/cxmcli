# Команда ниже возьмет ifc файл и заново перезапишет весь экспорт
#python ifcexport.py "examples/ifc/w7.ifc" \
#                    --name "export/w7" \


# Команда ниже возьмет ifc файл "./examples/ifc/w7.ifc" и запишет только те модели которые уже есть в "./export/w7
# Это нужно чтобы можно было удалить файлы ненужных слоев один раз, а после получать всегда чистую модель.
python ifcexport.py "examples/ifc/w7.ifc" \
                    --name "export/w7" \
                    --use-last


# Следующую команду нужно вызвать после любой из предыдущих. Для того чтобы загрузить геометрию во вьювер.
# Вы также можете поместить модель в конкретные сцены добавив дополнительные аргументы.
# Для этого смотрите файл "add_to_scene.sh"
python uploader.py "export/w7/w7_joined_all.json" \
                    --viewer-name w7-example \
                    --update \

# При режиме --update вместо --viewer-name можно передать --viewer-id
# Это не может работать в режиме --create, тк id еще не создан.
#python uploader.py "export/w7/w7_joined_all.json" \
#                    --viewer-id 93 \
#                    --update