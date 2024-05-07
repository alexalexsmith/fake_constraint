"""
fake constraint
by: Alex Smith
acts like a constraint without creating one to keep your scene cleaner
How it works:
Select 1 or more objects in the scene
Selecting 1 object to save that items offset compared to the world
Selecting 2 or more objects to save the offset between the first selection and the rest of the selection
run the copy_offset() command to copy the offset matrix and save it to a json file at users scripts folder
run the paste_offset() command to paste the copied offset back to those objects
pasting will occur on the current frame or across selected frames
"""
# TODO: add some arguments to the copy and paste functions to allow different functions like copy across a frame range

import json
import os

from maya import cmds, mel
import maya.api.OpenMaya as om


COPY_OFFSET_JSON_FILE = "FAKE_CONSTRAINT_COPY_OFFSET_JSON_FILE"


def copy_offset():
    """get the offset of an object in relation to another object or the world and write it out to a json file.
    The json file will be in the users scripts folder"""

    # Using selection to determine parent and child offset to calculate
    selection = cmds.ls(sl=True)

    if len(selection) < 1:
        cmds.warning("selection too small, select at least 1 object")
        return

    parent = None
    children_matrices = {}

    # If only one item is selected we calculate the items matrix in relation to the world
    if len(selection) == 1:
        children_matrices[selection[0]] = list(om.MMatrix(cmds.xform(selection[0], query=True, matrix=True, ws=True)))

    # If the selection is 2+, we calculate the offset between the first selection in relation to all other selections
    if len(selection) > 1:
        parent = selection[0]
        selection.remove(parent)
        children_matrices = get_matrices_offset_dict(parent, selection)

    data = {"parent": parent, "children_matrices": children_matrices}
    save_offset_to_json_file(data)


def paste_offset():
    """apply copied offset data at the current frame / selected frames"""

    copied_offset = read_offset_json_file()

    if copied_offset is None:
        return

    # Use the playback slider selected keys.
    # NOTE: If no frames are highlighted the range is current frame-current frame +1
    gPlayBackSlider = mel.eval("$fake_constraint_playback_slider = $gPlayBackSlider")
    frame_range = cmds.timeControl(gPlayBackSlider, query=True, rangeArray=True)

    # Normally these refresh and undo chunks would be decorators, but for the sake of making this a single file
    # I just wrote it like this
    cmds.refresh(suspend=True)
    cmds.undoInfo(openChunk=True)
    try:
        for frame in range(int(frame_range[0]), int(frame_range[1])):
            cmds.currentTime(frame)
            do_paste_offset(copied_offset)
    except Exception:
        raise
    finally:
        cmds.refresh(suspend=False)
        cmds.undoInfo(closeChunk=True)


def get_matrices_offset_dict(parent, children):
    """get the matrices offset dict
    :param str parent: parent to relate offset to
    :param list[str] children: children to compare
    :return dict: each key, named child, holding the offset matrix"""

    children_matrices = {}

    for child in children:
        # Using open maya to do the matrix math to get the offset
        parent_matrix = om.MMatrix(cmds.xform(parent, query=True, matrix=True, ws=True))
        child_matrix = om.MMatrix(cmds.xform(child, query=True, matrix=True, ws=True))
        offset_mmatrix = child_matrix * parent_matrix.inverse()
        children_matrices[child] = list(offset_mmatrix)

    return children_matrices


def get_user_scripts_folder():
    """get the maya users local scripts folder
    :return str: users maya scripts path. example C:/Users/UserName/Documents/maya/scripts/"""
    user_scripts_directory = cmds.internalVar(usd=True)
    mayas_scripts = '{0}/{1}'.format(user_scripts_directory.rsplit('/', 3)[0], 'scripts/')
    return mayas_scripts


def do_paste_offset_new(parent=None, children_matrices=None):
    """paste the offset to the child objects at the current frame
    :param str parent: name of parent
    :param dict children_matrices: dict of children matrices"""
    for child in children_matrices:
        if not cmds.objExists(child):
            continue

        # by default the paste matrix is the offset matrix in case we are doing a world snap
        offset_mmatrix = om.MMatrix(children_matrices[child])
        paste_matrix = offset_mmatrix

        if parent:
            if not cmds.objExists(parent):
                return

            # open maya matrix math to get the world position to set child in relation to parent
            parent_world_matrix = om.MMatrix(cmds.xform(parent, q=True, matrix=True, ws=True))
            paste_matrix = offset_mmatrix * parent_world_matrix

        cmds.xform(child, matrix=list(paste_matrix), ws=True)
        cmds.setKeyframe(child)

    return


def do_paste_offset(copied_offset):
    """paste the offset to the child objects at the current frame
    :param dict copied_offset: copied offset dict"""
    children_matrices = copied_offset["children_matrices"]
    for child in children_matrices:
        if not cmds.objExists(child):
            continue

        # by default the paste matrix is the offset matrix in case we are doing a world snap
        offset_mmatrix = om.MMatrix(children_matrices[child])
        paste_matrix = offset_mmatrix

        if copied_offset["parent"]:
            if not cmds.objExists(copied_offset["parent"]):
                return

            # open maya matrix math to get the world position to set child in relation to parent
            parent_world_matrix = om.MMatrix(cmds.xform(copied_offset["parent"], q=True, matrix=True, ws=True))
            paste_matrix = offset_mmatrix * parent_world_matrix

        cmds.xform(child, matrix=list(paste_matrix), ws=True)
        cmds.setKeyframe(child)


def save_offset_to_json_file(data):
    """save out the offset info to the scripts folder
    :param dict data: dictionary formatted data to write into json file"""

    file_path = "{0}{1}".format(get_user_scripts_folder(), COPY_OFFSET_JSON_FILE)
    with open(file_path, 'w') as outFile:
        json.dump(data, outFile, indent=4)


def read_offset_json_file():
    """read the offset info from the json file
    :return dict: contents of the json file"""

    file_path = "{0}/{1}".format(get_user_scripts_folder(), COPY_OFFSET_JSON_FILE)
    if not file_path or not os.path.isfile(file_path):
        return None

    with open(file_path) as json_data:
        json_file_contents = json.load(json_data)
    return json_file_contents
