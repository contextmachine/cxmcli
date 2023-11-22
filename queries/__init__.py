import json
import os

import requests
import click
import rich
import dotenv
dotenv.load_dotenv(".env")
URL=os.getenv("VIEWER_GRAPHQL_BACKEND_URL")
USER_ID=os.getenv("VIEWER_USER_ID")
HEADERS=json.loads(os.getenv("VIEWER_GRAPHQL_BACKEND_HEADERS"))

def check_gql_response(response):
    data = response.json()
    if 'data' in data.keys():
        return data
    else:
        raise ValueError(response.text)


def query(body, url=URL, headers=None, check_response=True):
    def call(**variables):
        nonlocal headers

        if headers is None:
            headers = HEADERS
        if not check_response:
            return requests.post(url, json=dict(query=body, variables=variables), headers=headers)
        else:
            return check_gql_response(requests.post(url, json=dict(query=body, variables=variables), headers=headers))

    return call


# language=GraphQl
update_query = """
mutation Update($data: jsonb = "", $id: Int = 1) {
  update_threejs_blobs_by_pk(pk_columns: {id: $id}, _set: {data: $data}) {
    id
    name
    update_at
  }
}

"""

# language=GraphQl
GetViewerBlobDataByName = query("""
query GetViewerBlobDataByName($name: String = "") {
  response:threejs_blobs(where: {name: {_eq: $name}}) {
    data
  }
}
""")
# language=GraphQl
GetViewerBlobIdByName = query("""
query GetViewerBlobIDByName($name: String = "") {
  response:threejs_blobs(where: {name: {_eq: $name}}) {
    id
    name

  }
}
""")
# language=GraphQl
GetViewerBlobNameByID = query("""
query GetViewerBlobNameByID($id: Int = "") {
  response:threejs_blobs(where: {name: {_eq: $id}}) {
    id
    name
  }
}
""")
# language=GraphQl
UpdateViewerBlobByName = query("""
mutation UpdateViewerBlobByName($name: String = "", $data: jsonb = "") {
  response:update_threejs_blobs(where: {name: {_eq: $name}}, _set: {data: $data}) {
    returning {
      id
      name
      update_at
    }
  }
}
""")
# language=GraphQl
UpdateViewerBlobById = query("""
mutation UpdateViewerBlobByID($id: Int, $data: jsonb = "") {
  response:update_threejs_blobs(where: {id: {_eq: $id}}, _set: {data: $data}) {
    returning {
      id
      name
      update_at
    }
  }
}
""")
# language=GraphQl
InsertViewerBlobByName = query("""
mutation InsertViewerBlobByName($name: String = "", $data: jsonb = "") {
  response:insert_threejs_blobs_one(object: {data: $data, name: $name}) {
    id
    name
    update_at
  }
}

""")

# language=GraphQl
AddViewerQuery = query("""
mutation UpdateViewerBlobByID($object: app_queries_insert_input = {}) {
  response: insert_app_queries_one(object: $object) {
    id
    title
    scene {
      title
    }
  }
}

""")
# language=GraphQl
GetViewerScenesByTitles = query("""
query GetViewerScenesByTitles($titles: [String!] = "") {
  response: app_scenes(where: {title: {_in: $titles}}) {
    id
    title
  }
}
""")
# language=GraphQl
GetViewerQueryByScenesAndTitle = query("""
query GetViewerScenesByTitle($title: String = "", $scenes_id: [uuid!] = "") {
  response: app_queries(where: {title: {_eq: $title}, scene_id: {_in: $scenes_id}}) {
    id
    scene_id
    title
  }
}



""")