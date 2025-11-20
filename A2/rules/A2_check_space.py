#I want to check if the desks in office spaces 
import ifcopenshell as ifc
import ifcopenshell.util.classification
import ifcopenshell.util.selector
import re, os
from collections import defaultdict
import numpy as np
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


######################### DESKS IN SPACES ###########################
#the relevant elements that will be worked with:
spaces = model.by_type("IfcSpace")
doors = model.by_type("IfcDoor")
storey = model.by_type("IfcBuildingStorey")


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
for space in spaces:
    print(space)
    desks_in_space = []
    for rel in model.get_inverse(space):
        if rel.is_a("IfcRelContainedInSpatialStructure"):
            for element in rel.RelatedElements:
                if is_desk(element):
                    desks_in_space.append(element)

    print(f"Space: {space.Name or space.GlobalId}")
    if desks_in_space:
        print(f"  → Found {len(desks_in_space)}")
        deskSpaces.append(space)
    else:
        print("  → No desks found.")
#COMMENTS
#We iterate through all spaces in the model
#We use .get_inverse to find where the space is referenced in IfcRelContainedInSpatialStructure relationships
#Then we check the RelatedElements of those relationships to see if any are desks
#If desks are found, we add the space to 'deskSpaces = []' list

def get_storey_for_space(model, space):
    to_visit = [space]
    visited = set()
    while to_visit:
        obj = to_visit.pop()
        if obj in visited:
            continue
        visited.add(obj)

        for rel in model.get_inverse(obj):
            # Space contained in a spatial structure (storey, building, etc.)
            if rel.is_a("IfcRelContainedInSpatialStructure"):
                container = rel.RelatingStructure
                if container.is_a("IfcBuildingStorey"):
                    return container
                to_visit.append(container)

            # Or space might be aggregated into something that is on a storey
            elif rel.is_a("IfcRelAggregates"):
                container = rel.RelatingObject
                if container.is_a("IfcBuildingStorey"):
                    return container
                to_visit.append(container)

    return None

#textfile generation
with open("A2/A2_analyst_checks_GRP2.txt", "w") as f:
    f.write("I have analysed desks in the office spaces in the ifc model.\n")
    f.write("I have done so in accordance to 'Arbejdstilsynet' the governmental body regulating working spaces.\n")
    f.write("Guidelines from Arbejdstilsynet:\n")
    f.write(" - The height to the ceiling in the office space must be at least 2.5 meters.\n")
    f.write(" - The floor area must be at least 7 m2.\n")
    f.write(" - There must be 12 m3 of air in the work space per person.\n")
    f.write(" - Length of desks should be 117 cm.\n")
    f.write(" - Link to guidelines: https://regler.at.dk/at-vejledninger/arbejdspladsens-indretning-inventar-a-1-15/ \n")
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

        # find the storey (IfcBuildingStorey) for this space
        storey_name = storey.Name if storey and getattr(storey, "Name", None) else "UNKNOWN_STOREY"

        space_name = getattr(space, "Name", "") or "UNNAMED_SPACE"

        # write one line per space
        f.write(f"  - Storey name: {storey_name}\n")
        f.write(f"  - Space name: {space_name}\n")
        f.write(f"  - No. of desks in this: {desk_count}\n")
            

        if 'Dimensions' in psets:
            dimensions = psets['Dimensions']
            height = dimensions.get('Unbounded Height', 'N/A')
            floor_area = dimensions.get('Area', 'N/A')
            floor_area_desk = floor_area / len(desks_in_space)
            volume_per_desk = (height * floor_area_desk)
            #Here we find the desk dimensions, however there is no 'length property' in the pset
            #There is a desk length in the name of the element though...
            desk_length = dimensions.get('Length', 'N/A')

            
            f.write(f"  - Height: {round(height*pow(10, -3),2)} m\n")
            f.write(f"  - Area: {round(floor_area,2)} m2\n")
            f.write(f"  - Volume per desk: {round(volume_per_desk* pow(10, -3), 2)} m3\n")
            f.write(f"  - Area per desk: {round(floor_area_desk,2)} m2\n")
            f.write(f"  - Length of desk: {desk_length} mm\n")

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
    print(sp)
    for space in sp:
        desks_in_space = []
        for rel in model.get_inverse(space):
            if rel.is_a("IfcRelContainedInSpatialStructure"):
                for element in rel.RelatedElements:
                    if is_desk(element):
                        desks_in_space.append(element)

        print(f"Space: {space.Name or space.GlobalId}")
        if desks_in_space:
            print(f"  → Found {len(desks_in_space)}")
            door_width_sum = 0
            for d in doors_in_space:
                pset = ifcopenshell.util.element.get_psets(d)
                door_width_sum += pset['Dimensions']['Width']
            fireSafety_numberdesks_widthdoor = door_width_sum / len(desks_in_space)
            print(f'  → Safety check (cm door width per desk): {fireSafety_numberdesks_widthdoor} mm')



""" for b in model.by_type("IfcRelSpaceBoundary"):
        for relbounded in b.BoundedBy:
            sp = b.RelatingSpace
            el = b.RelatedBuildingElement
            print(sp, el)

 """