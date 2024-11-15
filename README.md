# **Fake Constraint Script**

Python tool that acts like a parent constraint without creating a parent constraint node.
Tested in Maya 2018, 2022 and 2023 with python 2 and python 3. It should work in Maya 2016 too.
I created this tool as a 1 stop solution for all my foot snapping, constraint toggling and baking. It's simple to use and really fast. My favorite part about this tool is I can add the commands to hotkeys, marking menus, etc... I hope you find it as useful as I do!

## **Installation**
place the fake_constraint.py file into your scripts folder

## **How to use it:**
-Select 1 or more objects

-run this python command to copy the offset
`import fake_constraint;fake_constraint.copy_offset()`

-run this python command to paste the offset
`import fake_constraint;fake_constraint.paste_offset()`

Selecting 1 object copies the world position(world snap).

Selecting 2 or more objects copies the offset in relation to the first selected object and the other objects.

Pasting will occur on the current frame or across selected frames.

## **How to use it in a marking menu:**

Since maya's marking menus only allow mel commands you'll need to run the python commands through mel with the python mel command.

`python("import fake_constraint;fake_constraint.copy_offset()")`

`python("import fake_constraint;fake_constraint.paste_offset()")`

## **How it works:**
The tool uses Mayas OpenMaya api to calculate the offset matrix between the objects. It saves the offset to a json file at the users scripts folder. The paste function reads in the json file and uses matrix math to set the positions of each object relative to the "parent"

## **Contact**
If you have any bugs, questions or anything you can email me at alexgsmith800@gmail.com
