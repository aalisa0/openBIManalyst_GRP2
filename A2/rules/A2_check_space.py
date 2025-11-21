#I want to check if the desks in office spaces 
import ifcopenshell as ifc
import ifcopenshell.util.classification
import ifcopenshell.util.selector
import re, os
from collections import defaultdict
import numpy as np
import json
#import pandas as pd


############################ LOAD IFC FILE #############################
#Load IFC files from the current directory
pattern = r".*\.ifc$"  # Match all files ending with ".ifc"

list_of_ifc_files = []

cnt = 1

for filename in os.listdir("."):
    if re.search(pattern, filename):
        print(str(cnt)+".", filename)
        list_of_ifc_files.append(filename)
        cnt += 1

#what the user is asked
modelChoice = int(input("\nWhich ifc file do you want to use? (Please enter the number corresponding to the file):\n"))

#write # in the terminal to load the file you want
#Load IFC file
model = ifc.open(list_of_ifc_files[modelChoice - 1])



#the relevant elements that will be worked with:
spaces = model.by_type("IfcSpace")
doors = model.by_type("IfcDoor")
storey = model.by_type("IfcBuildingStorey")


######################### DESKS IN SPACES ###########################

#Function to identify if an element is a desk
def is_desk(element):
    if element.is_a("IfcBuildingElementProxy") or element.is_a("IfcFIfcFurniture"):
        name = (element.Name or "").lower()
        obj_type = (element.ObjectType or "").lower()
        return "desk" in name or "desk" in obj_type
    return False
#COMMENTS
#we are looking through the catagory of IfcBuildingElementProxy and IfcFurniture
#and checking if an element has 'desk' in its name or object type


#A list to store spaces with desks
deskSpaces = []
#Iterate through spaces and check for desks and print quantity


#Func. to count no. of desks in spaces in and outside spaces 
#we call this in line 
def no_of_desks_in_space(spaces, toAppend=True):
    sum = 0
    for space in spaces:
        desks_in_space = []
        for rel in model.get_inverse(space):
            if rel.is_a("IfcRelContainedInSpatialStructure"):
                for element in rel.RelatedElements:
                    if is_desk(element):
                        desks_in_space.append(element)
                        
        print(f"Space: {space.Name or space.GlobalId}")
        if desks_in_space:
            print(f"  → Found {len(desks_in_space)}")
            sum += len(desks_in_space)
            if toAppend:
                deskSpaces.append(space)
        else:
            print("  → No desks found.")
    print(f"\nTotal number of desks in model: {sum}")
    if toAppend:
        f.write(f"\nTotal of desks in spaces: {sum}\n")
    else:
        f.write(f"Total of desks outside spaces: {sum}\n")
        


#COMMENTS
#We iterate through all spaces and storyes  in the model
#We use .get_inverse to find where the space is referenced in IfcRelContainedInSpatialStructure relationships
#Then we check the RelatedElements of those relationships to see if any are desks
#If desks are found, we add the space to 'deskSpaces = []' list

def pset_for_desk_spaces():
    for space in deskSpaces:
        f.write(f"\nSpace: {space.Name or space.GlobalId}\n")
        #Quantities are found in the property sets ('psets') of the spaces
        psets = ifcopenshell.util.element.get_psets(space)
        
        #Finds no. of desks in space
        desks_in_space = []
        for rel in model.get_inverse(space):
            if rel.is_a("IfcRelContainedInSpatialStructure"):
                for element in rel.RelatedElements:
                    if is_desk(element):
                        desks_in_space.append(element)
        desk_count = len(desks_in_space)

        doors = space_to_doors[space]
        doorString = ""
        door_width = 0
        for d in doors:
            door_pset = ifcopenshell.util.element.get_psets(d)
            door_width += door_pset['Dimensions']['Width']


        if 'Dimensions' in psets:
            constraints = psets['Constraints']
            dimensions = psets['Dimensions']
            height = dimensions.get('Unbounded Height', 'N/A')
            floor_area = dimensions.get('Area', 'N/A')
            floor_area_desk = floor_area / len(desks_in_space)
            volume_per_desk = (height * floor_area_desk)
            #Here we find the desk dimensions, however there is no 'length property' in the pset
            #There is a desk length in the name of the element though...
            desk_length = dimensions.get('Length', 'N/A')
            floor = constraints.get('Level')

            f.write(f"  - No. of desks in this space: {desk_count}\n")
            f.write(f"  - Floor: {floor}\n")
            f.write(f"  - Height: {round(height*pow(10, -3),2)} m\n")
            f.write(f"  - Area: {round(floor_area,2)} m2\n")
            f.write(f"  - Volume per desk: {round(volume_per_desk* pow(10, -3), 2)} m3\n")
            f.write(f"  - Area per desk: {round(floor_area_desk,2)} m2\n")
            f.write(f"  - Length of desk: {desk_length} mm\n")
            f.write(f"  - No. of doors: {len(doors)}\n")
            f.write(f"  - Total door width: {door_width}\n")
            f.write(f"  - Desk to door width ratio: {door_width / desk_count}\n")

        else:
            f.write("  - No Dimensions Pset found.\n")


###################### DOORS AND DESKS ###########################

settings = ifcopenshell.geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)
def get_vertices(product):
    shape = ifcopenshell.geom.create_shape(settings, product)
    verts = np.array(shape.geometry.verts, dtype=float).reshape(-1, 3)
    return verts
def get_bbox(product):
    verts = get_vertices(product)
    minv = verts.min(axis=0)  # [min_x, min_y, min_z]
    maxv = verts.max(axis=0)  # [max_x, max_y, max_z]
    return minv, maxv
def get_door_midpoint(door):
    minv, maxv = get_bbox(door)
    mid = (minv + maxv) / 2.0
    return mid  # np.array([x, y, z])

space_boxes = {}  # key: IfcSpace, value: (minv, maxv)

for sp in spaces:
    try:
        minv, maxv = get_bbox(sp)
        space_boxes[sp] = (minv, maxv)
    except Exception as e:
        print(f"Could not compute bbox for space {sp.GlobalId}: {e}")

def point_in_box(point, minv, maxv, margin=-0.5):
    """
    Check if point is inside axis-aligned bounding box [minv, maxv].
    margin > 0 shrinks the box a bit, margin < 0 expands it.
    """
    return (
        (minv[0] + margin) <= point[0] <= (maxv[0] - margin) and
        (minv[1] + margin) <= point[1] <= (maxv[1] - margin) and
        (minv[2] + margin) <= point[2] <= (maxv[2] - margin)
    )


##################### DOOR TO SPACE MAPPING #######################
space_to_doors = defaultdict(list)

# door -> space (if you want reverse mapping)
door_to_space = {}

for door in doors:
    try:
        mid = get_door_midpoint(door)
    except Exception as e:
        print(f"Could not compute midpoint for door {door.GlobalId}: {e}")
        continue

    assigned_space = None

    for sp, (minv, maxv) in space_boxes.items():
        if point_in_box(mid, minv, maxv):
            assigned_space = sp
            space_to_doors[sp].append(door)
            door_to_space[door] = sp
            break

    if assigned_space is None:
        # Midpoint not inside any IfcSpace
        print(f"Door {door.GlobalId} is not inside any IfcSpace (by midpoint).")


deskSpacesNames = [space.Name for space in deskSpaces] 
for sp, doors_in_space in space_to_doors.items():
    space_name = sp.Name or sp.GlobalId
    if space_name in deskSpacesNames:
        print(f"\nSpace {space_name} ({sp.GlobalId}) has {len(doors_in_space)} door(s):")
        
        for d in doors_in_space:
            door_name = d.Name or d.Tag or d.GlobalId
            print(f"  - Door {door_name} ({d.GlobalId})")
    desks_in_space = []
    for rel in model.get_inverse(sp):
        if rel.is_a("IfcRelContainedInSpatialStructure"):
            for element in rel.RelatedElements:
                if is_desk(element):
                    desks_in_space.append(element)

    print(f"Space: {sp.Name or sp.GlobalId}")
    if desks_in_space:
        print(f"  → Found {len(desks_in_space)}")
        door_width_sum = 0
        for d in doors_in_space:
            pset = ifcopenshell.util.element.get_psets(d)
            door_width_sum += pset['Dimensions']['Width']
        fireSafety_numberdesks_widthdoor = door_width_sum / len(desks_in_space)
        print(f'  → Safety check (cm door width per desk): {fireSafety_numberdesks_widthdoor} mm')



############### CALL JSON #################
guidelines = {}
with open("A2/test.json") as file:
    guidelines = json.load(file)


################### TEXT FILE GENERATION ##########################

with open("A2/A2_analyst_checks_GRP2.txt", "w") as f:
    for line in guidelines["guidelines"]:
        f.write(line)


##################### DESK QUANTITIES AND DIMENSIONS ###########################

    #call the function 
    no_of_desks_in_space(spaces)
    #call the function again without appending to deskSpaces. Because there are desks outside of spaces in the model!
    no_of_desks_in_space(storey, False)
    pset_for_desk_spaces()









