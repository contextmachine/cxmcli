import json
import os

from queries import *


def upload_new_blob(name: str, data: dict):
    response = InsertViewerBlobByName(name=name, data=data)
    return check_gql_response(response)


def update_exist_blob_by_name(name: str, data: dict):
    response = UpdateViewerBlobByName(name=name, data=data)
    return check_gql_response(response)


def update_exist_blob_by_id(id: int, data: dict):
    response = UpdateViewerBlobByName(id=id, data=data)
    return check_gql_response(response)


def add_blob_to_scene(scene_id: str, blob_name: str, title: str, user_id: str = USER_ID):
    # language=GraphQl
    temp_viewer_query = """
query GetViewerBlobByName($name: String = "%") {
  response: threejs_blobs(where: {name: {_eq: $name}}) {
    data
  }
}
    """
    temp_viewer_query = temp_viewer_query.replace('%', blob_name)

    return AddViewerQuery(object={
        "scene_id": scene_id,
        "title": title,
        "type": "gql",
        "update_author_id": user_id,
        "update_type": "entire",
        "author_id": user_id,
        "body": {
            "query": temp_viewer_query,
            "endpoint": "https://viewer.contextmachine.online/v1/graphql"
        }

    })


def add_to_scenes(scenes_id, blob, title, user_id: str = USER_ID):
    for scene_id in scenes_id:
        yield add_blob_to_scene(scene_id=scene_id,
                                blob_name=blob['name'],
                                title=title,
                                user_id=user_id)


@click.command()
@click.argument('source')
@click.option('--viewer-name', default='', help="Имя модели для запросов из вьювера. Строка")
@click.option('--viewer-id', default=-1, help="Id модели для запросов из вьювера. Целое число.")
@click.option('--update', is_flag=True, default=False,
              help="Выберите эту опцию если хотите обновить существующую модель (предпочтительно всегда когда модель уже существует). "
                   "Для обновления можно использовать как --viewer-name так и --viewer-id")
@click.option('--create', is_flag=True, default=False, help="Выберите эту опцию если хотите добавить новую модель. "
                                                            "\nВключение этой опции также обязует вас задать опцию "
                                                            "--viewer-name."
                                                            "\nОпция --viewer-id будет проигнорирована, вместо чего, после выполнения вам вернется id, созданной вами записи."
              )
@click.option('--scene', multiple=True,
              help="Добавит модель в сцену с соответствующим именем. Если имя сцены дублируется добавит во все сцены. "
                   "\nАргумент может быть использован несколько раз.")
@click.option('--title', default="BY_NAME",
              help="Определяет название модели в сцене. По умолчанию идентичен значению --viewer-name.")
def upload_blob(source, viewer_name, viewer_id, update, create, scene, title):
    if all([not create, not update]):

        resp = GetViewerBlobNameByID(id=viewer_id) if viewer_id != -1 else GetViewerBlobIdByName(name=viewer_name)

        blob = resp['data']['response'][0]
        rich.print(resp)


    else:
        with open(source, 'r') as f:
            data = json.load(f)
        if create:
            resp = InsertViewerBlobByName(name=viewer_name, data=data)

            blob = resp['data']['response']
        elif update:
            if viewer_name:
                resp = UpdateViewerBlobByName(name=viewer_name, data=data)
            else:
                resp = UpdateViewerBlobById(id=viewer_id, data=data)

            blob = resp['data']['response']['returning'][0]

    if scene:

        if title == "BY_NAME":
            title = blob['name']
        scenes = GetViewerScenesByTitles(titles=scene)['data']['response']
        scene_attrs = dict()
        for item in scenes:
            for key, val in item.items():
                if key not in scene_attrs:
                    scene_attrs[key] = []
                scene_attrs[key].append(val)

        for item in GetViewerQueryByScenesAndTitle(title=title, scenes_id=scene_attrs['id'])['data']['response']:
            if item['scene_id'] in scene_attrs['id']:
                i = scene_attrs['id'].index(item['scene_id'])
                scene_attrs['id'].remove(item['scene_id'])
                rich.print(f'Query {item["title"]} is exist in {scene_attrs["title"][i]} scene!')

        if len(scene_attrs['id']) > 0:
            for response in add_to_scenes(scenes_id=scene_attrs['id'],
                                          blob=blob,
                                          title=title,
                                          user_id=USER_ID):
                rich.print(response)


if __name__ == '__main__':
    upload_blob()
