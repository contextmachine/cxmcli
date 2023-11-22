import json
import random
import uuid
import os
import ifcopenshell
import numpy as np
import ujson
from ifcopenshell import geom
from OCC.Core.Tesselator import ShapeTesselator
from mmcore.base import AGroup, AMesh
from mmcore.geom.materials import ColorRGB
from mmcore.base import create_buffer_from_dict
from pathlib import Path
import os

NAME = "export"
EXPORT_PATH = f"{os.getcwd()}/mm-ifcexport"
from mmcore.geom.plane import create_plane, world_to_local, local_to_world, vectorize, rotate_plane
from mmcore.base.models.gql import create_shape_buffer, update_shape_buffer, create_material, create_uvlike_buffer, \
    MeshPhongMaterial, create_buffer_color
from mmcore.geom.mesh import MeshTuple, union_mesh, create_mesh_tuple

from mmcore.compat.gltf.convert import create_union_mesh_node, create_scene_from_meshes, asscene


def create_union_mesh(uuid, meshes, ks=('position',)):
    r = union_mesh(meshes, ks)
    vm = create_material(amatdict, uuid + '-mat', (250, 250, 250), vertexColors=True)
    m = AMesh(uuid=uuid,
              geometry=create_shape_buffer(uuid + '-geom',
                                           position=r.attributes['position'].tolist(),
                                           color=r.attributes['color'].tolist(),
                                           index=r.indices.tolist()),

              material=vm)
    m.add_userdata_item('parts', r.extras['parts'].tolist())
    return m


vertexMaterial = MeshPhongMaterial(uuid='vxmat', color=ColorRGB(200, 200, 200).decimal, vertexColors=True, side=2)


def props(f):
    props = dict(context=f.data.context, type=f.data.type, parent_id=f.data.parent_id)
    for k in f.data.product.get_attribute_names():
        val = f.data.product.get_argument(k)

        props[k] = f'{val}'

    return props


from mmcore.base.registry import objdict, amatdict, ageomdict

cb = lambda nam: nam.split(":")[0]

DISABLE_TRIANGULATION = True
NO_WIRE_INTERSECTION_CHECK = True
COMPRESSED = False


def thr(source, path=EXPORT_PATH, prefix=NAME, file_names=()):
    colors = {}
    nms = {}

    support_attributes = dict()

    fl = ifcopenshell.open(source)
    settings = geom.settings(USE_PYTHON_OPENCASCADE=True, DISABLE_TRIANGULATION=True,
                             NO_WIRE_INTERSECTION_CHECK=NO_WIRE_INTERSECTION_CHECK)

    itr = geom.iterate(file_or_filename=fl, settings=settings)

    for i, o in enumerate(itr):

        try:

            _name = cb(o.data.name)
            if any([_name == "", _name is None]):
                _name = f"Undefined-{i}"

            _name = _name.replace("/", "-").replace("\\", "-")
            if _name not in nms.keys():
                nms[_name] = []
                if o.styles:
                    r, g, b, a = o.styles[0]
                    colors[_name] = r, g, b
                else:
                    colors[_name] = random.random(), random.random(), random.random()

                # amatdict[hex(hash(_name)) + "_mat"] = AMesh.material_type(uuid=hex(hash(_name)) + "_mat",
                # color=colors[_name])
            gmuid = uuid.uuid4().hex

            tess = ShapeTesselator(o.geometry)
            tess.Compute(compute_edges=False,
                         mesh_quality=1.0,
                         parallel=True)

            data = json.loads(tess.ExportShapeToThreejsJSONString(gmuid))
            attributes = dict()
            ixs = None

            for k, d in data['data']['attributes'].items():
                # buff[k].extend(d['array'])

                # _parts.extend((np.ones(len(d['array']))*mn).tolist())

                attributes[k] = d['array']
            if 'index' in data['data']:
                ixs = data['data']['array']

            msh = create_mesh_tuple(attributes, ixs, color=colors[_name])
            if not (len(_name) > 0):
                _name = uuid.uuid4().hex
            support_attributes[_name] = list(attributes.keys()) + ['color']
            nms[_name].append(msh)

            print(f'export {i} item {_name}', flush=True, end="\r")
        except Exception as err:
            print(err)
            pass

    print("\nbuilding meshes ...")
    meshes = build_meshes(nms=nms,
                          support_attributes=support_attributes,
                          filenames=file_names)
    print("\ndump to filesystem ...")
    dump_all_to_fs(path=path,
                   name=prefix,
                   meshes=meshes,
                   support_attributes=support_attributes)

    print("done!\n")


def dump_group(name, nms):
    return nms[name].root()


def build_mesh_with_buffer(mesh: MeshTuple, name: str):
    uid = uuid.uuid4().hex

    create_uvlike_buffer(amatdict, **{k: attr.tolist() for k, attr in mesh.attributes.items()},
                         uuid=uid)
    return AMesh(uuid=uid + 'mesh',
                 name=name,
                 geometry=ageomdict[uid],
                 material=vertexMaterial)


def build_meshes(nms, support_attributes, filenames=()) -> dict:
    meshes = dict()
    names = []

    for k, n in nms.items():

        if len(filenames) > 0:

            if k in filenames:
                names.append(k)
                u = union_mesh(n, support_attributes[k])
                meshes[k] = u


        else:

            u = union_mesh(n, support_attributes[k])

            meshes[k] = u

    return meshes


def dump_all_to_fs(path, name, meshes, support_attributes):
    grp = AGroup(uuid=f'{name}-group', name=name)
    for k, msh in meshes.items():
        amesh = build_mesh_with_buffer(msh, k)
        amesh.dump(f"{path}/{k}.json")
        grp.add(amesh)
    grp.dump(path + '/' + name + "_all.json")
    all_attrs = tuple(set.intersection(*(set(val) for val in support_attributes.values())))
    print(all_attrs)
    joined = union_mesh(list(meshes.values()), all_attrs)
    amesh = build_mesh_with_buffer(joined, name)
    amesh.dump(path + '/' + name + "_joined_all.json")


import click
from datetime import datetime


def export_file(source, name, use_last):
    file_names = []
    if name == "FROM_SOURCE":
        target_path = source.split('/')[-1].split('.')[0]
    else:
        target_path = name
    prefix = target_path.split('/')[-1]
    if not os.path.exists(target_path):
        Path(target_path).mkdir(parents=True, exist_ok=True)
    else:
        if use_last:
            for fl in os.scandir(target_path):
                file_names.append(fl.name.replace('.json', ''))

    thr(source=source, prefix=prefix, path=target_path, file_names=file_names)


import rich

import multiprocess as mp
def _export_file_mp(args):
    source, name, use_last=args
    export_file(source, name, use_last)
def exporter(source, name, multiply, use_last):


    if multiply:
        print('🛠️ prepare multiply export ...')
        sources = []
        for item in os.scandir(source):
            if item.name.lower().endswith('.ifc'):
                sources.append((item.path, f'{name}/{item.name}',use_last))
        print("\n" + ('-' * 140) + '\ntasks:\n\n')
        rich.print(sources)
        print('starting... \n')
        with mp.Pool(len(sources)) as pool:
            pool.map(_export_file_mp, sources)


    else:
        print(f"🛠️ {source} -> {name}")
        export_file(source=source,
                    name=name,
                    use_last=use_last)
    print('-' * 80 + '\n🛠 all tasks done!')


@click.command()
@click.argument('source')
@click.option('--name', default="FROM_SOURCE",
              help='Абсолюютный или относительный путь до директории в которую следует экспортировать модель. '
                   '\nЗначение FROM_SOURCE заставит скрипт использовать имя текущего '
                   '\nфайла в качестве имени директории. Будте аккуратны, '
                   '\nесли имя файла содержит различные недопустимые символы, '
                   '\nтакие как: [\\/,.] или не символы utf-8, экспорт может '
                   '\nзакончиться ошибкой.\n\n')
@click.option('--multiply', is_flag=True, default=0, help='Включает опцию мульти-экспорта. Переданный первым '
                                                          '\nаргументом путь будет воспринят как путь к директории. Все '
                                                          '\nнаходящиеся там файлы, как файлы ifc. Директория не должна '
                                                          '\nсодержать ничего кроме файлов предназначенных для экспорта. '
                                                          '\nОпция --name в данном случае будет использоваться как '
                                                          '\nкорневая директория экспорта.\n\n')
@click.option('--use-last', is_flag=True, default=0, help='Будут сохранены только те файлы которые уже находятся в '
                                                          '\nэкспортной папке. Остальные будут проигнорированы.\n\n')
def cli(source, name, multiply, use_last):
    print('🛠️ arguments: \n')
    rich.print(dict(source=source, name=name, multiply=multiply, use_last=use_last))
    exporter(source, name, multiply, use_last)


if __name__ == "__main__":
    cli()
