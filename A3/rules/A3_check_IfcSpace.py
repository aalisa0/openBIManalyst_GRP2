#I want to check if the desks in office spaces 
import ifcopenshell as ifc
import ifcopenshell.util.classification
import ifcopenshell.util.selector
import re, os
from collections import defaultdict
import numpy as np
import json
import matplotlib.pyplot as plt
import os
#import pandas as pd




############################ LOAD ANY IFC FILE #############################
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
#write # in the terminal to load the file you want
modelChoice = int(input("\nWhich ifc file do you want to use? (Please enter the number corresponding to the file):\n"))



#Open the selected IFC file
model = ifc.open(list_of_ifc_files[modelChoice - 1])



#the relevant elements that will be worked with:
spaces = model.by_type("IfcSpace")
doors = model.by_type("IfcDoor")
storey = model.by_type("IfcBuildingStorey")

desks_in_spaces_count = 0         
desks_outside_spaces_count = 0     
desks_per_level = defaultdict(int) 
desks_area_above_7 = 0            
desks_area_7_or_below = 0   



######################### DESKS IN SPACES ###########################

#Function to identify if an element is a desk
def is_desk(element):
    if element.is_a("IfcBuildingElementProxy") or element.is_a("IfcFurniture"):
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
def no_of_desks_in_space(spaces, toAppend=True):
    total_desks = 0
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
            total_desks+= len(desks_in_space)
            if toAppend:
                deskSpaces.append(space)
        else:
            print("  → No desks found.")
    print(f"\nTotal number of desks in model: {total_desks}")
    if toAppend:
        f.write(f"\nTotal of desks in spaces: {total_desks}\n")
    else:
        f.write(f"Total of desks outside spaces: {total_desks}\n")
    return total_desks
#COMMENTS
#We iterate through all spaces and storyes  in the model
#We use .get_inverse to find where the space is referenced in IfcRelContainedInSpatialStructure relationshipss
#Then we check the RelatedElements of those relationships to see if any are desks
#If desks are found, we add the space to 'deskSpaces = []' list

def pset_for_desk_spaces():
    global desks_per_level, desks_area_above_7, desks_area_7_or_below
    for space in deskSpaces:
        f.write(f"\nSpace: {space.Name or space.GlobalId}\n")
        psets = ifcopenshell.util.element.get_psets(space)
        
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
            if isinstance(floor_area, (int, float)) and desk_count > 0 and isinstance(height, (int, float)):  
                floor_area_desk = floor_area / desk_count
                volume_per_desk = height * floor_area_desk
                floor = constraints.get('Level', 'Unknown')
                desks_per_level[floor] += desk_count  

                # area per desk statistics (for > 7 m²)
                if floor_area_desk >= 7:              
                    desks_area_above_7 += desk_count
                else:
                    desks_area_7_or_below += desk_count



                floor_area_desk = floor_area / len(desks_in_space)
                volume_per_desk = (height * floor_area_desk)
                #Here we find the desk dimensions, however there is no 'length property' in the pset
                #There is a desk length in the name of the element though...
                desk_length = dimensions.get('Length', 'N/A')
                floor = constraints.get('Level')

                f.write(f"  - No. of desks in this space: {desk_count}\n")
                f.write(f"  - Floor: {floor}\n")
                f.write(f"  - Height of space: {round(height*pow(10, -3),2)} m\n")
                f.write(f"  - Area: {round(floor_area,2)} m2\n")
                f.write(f"  - Volume per desk: {round(volume_per_desk* pow(10, -3), 2)} m3\n")
                f.write(f"  - Area per desk: {round(floor_area_desk,2)} m2\n")
                f.write(f"  - Length of desk: {desk_length} mm\n")
                f.write(f"  - No. of doors: {len(doors)}\n")
                f.write(f"  - Total door width (internal): {round(door_width* pow(10, -1),2)} cm\n")
                f.write(f"  - Desk to door width ratio: {round((door_width / desk_count)* pow(10, -1),2)} cm\n")
            else:
                f.write("  - Dimensions missing or not numeric, skipped stats.\n")

        else:
            f.write("  - No Dimensions Pset found.\n")
# COMMENTS
#Quantities are found in the property sets ('psets') of the spaces
#then we write these quantities to the text file
#round is used to limit decimal places for easier reading
#the floor level is found in the Constraints pset which is seen in the blender file 



###################### FIND DOORS BY MIDPOINT ###########################

settings = ifcopenshell.geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)
def get_vertices(product):
    shape = ifcopenshell.geom.create_shape(settings, product)
    verts = np.array(shape.geometry.verts, dtype=float).reshape(-1, 3)
    return verts
def get_bbox(product):
    verts = get_vertices(product)
    minv = verts.min(axis=0)  
    maxv = verts.max(axis=0)  
    return minv, maxv
def get_door_midpoint(door):
    minv, maxv = get_bbox(door)
    mid = (minv + maxv) / 2.0
    return mid  

space_boxes = {}  

for sp in spaces:
    try:
        minv, maxv = get_bbox(sp)
        space_boxes[sp] = (minv, maxv)
    except Exception as e:
        print(f"Could not compute bbox for space {sp.GlobalId}: {e}")

def point_in_box(point, minv, maxv, margin=-0.5):
    return (
        (minv[0] + margin) <= point[0] <= (maxv[0] - margin) and
        (minv[1] + margin) <= point[1] <= (maxv[1] - margin) and
        (minv[2] + margin) <= point[2] <= (maxv[2] - margin)
    )

#COMMENTS 
#here we make a box around each space using its bounding box
#then we check if the IfcDoor midpoint is inside any of these boxes
#the margin is set to -0.5 so the box is bigger than the IfcSPace and finds the doors 
#the -0.5 margin is in meters (500mm)
#Spaceboxes is a dictionary instead of a list to map spaces to their bounding boxes


##################### SPACES WITH DOORS DIVIDE BY NO DESKS  #######################
space_to_doors = defaultdict(list)
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
        #Check if midpoint not inside/close to any IfcSpace printed in termenal
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


def report_spaces_without_desks(f, spaces, deskSpaces):
    spaces_with_desks = set(deskSpaces)
    spaces_without_desks = [sp for sp in spaces if sp not in spaces_with_desks]

    f.write("\n\n==================== SPACES WITH NO DESKS ====================\n")
    if spaces_without_desks:
        for sp in spaces_without_desks:
            f.write(f"  - {sp.Name or sp.GlobalId}\n")
    else:
        f.write("  All spaces have at least one desk.\n")


def report_desks_without_spaces(f, model, deskSpaces):
    all_desks = []
    for elem in model.by_type("IfcBuildingElementProxy"):
        if is_desk(elem):
            all_desks.append(elem)
    for elem in model.by_type("IfcFurniture"):
        if is_desk(elem):
            all_desks.append(elem)

    desks_in_spaces = set()
    for sp in deskSpaces:
        for rel in model.get_inverse(sp):
            if rel.is_a("IfcRelContainedInSpatialStructure"):
                for element in rel.RelatedElements:
                    if is_desk(element):
                        desks_in_spaces.add(element)

    # desks in model but not in any space
    desks_without_space = [d for d in all_desks if d not in desks_in_spaces]

    f.write("\n\n================ DESKS NOT IN ANY 'IfcSpace' ================\n")
    if desks_without_space:
        for d in desks_without_space:
            desk_name = d.Tag or d.Name or d.ObjectType or "Unknown"
            desk_id = d.GlobalId

            f.write(f"  - Desk: {desk_name}  (GlobalId: {desk_id})\n")

    else:
        f.write("  All desks are assigned to a space.\n")



############# MAKE SURE THAT THERE IS A FOLDER FOR THE TXT FILE ##############
os.makedirs("A3", exist_ok=True)


############### CALL JSON GUIDELINES FILE #################
guidelines = {}
with open("A3/guide.json") as file:
    guidelines = json.load(file)


################### TEXT FILE GENERATION ##########################
with open("A3/A3_analyst_checks_GRP2.txt", "w") as f:
    for line in guidelines["guidelines"]:
        f.write(line)


##################### CALL FUNCTIONS ###########################
    #call the function
    desks_in_spaces_count = no_of_desks_in_space(spaces)
    #call the function again without appending to deskSpaces. Because there are desks outside of spaces in the model!
    desks_outside_spaces_count = no_of_desks_in_space(storey, False)
    pset_for_desk_spaces()
    report_spaces_without_desks(f, spaces, deskSpaces)
    report_desks_without_spaces(f, model, deskSpaces)

##################### MAKE PLOTS ###########################

def make_plots():
    # use the global stats already computed
    global desks_in_spaces_count, desks_outside_spaces_count
    global desks_per_level, desks_area_7_or_below, desks_area_above_7

    desks_in_spaces = desks_in_spaces_count
    desks_outside_spaces = desks_outside_spaces_count

    # 1) Pie chart: desks in spaces vs outside spaces
    plt.figure()
    plt.title("Desks in spaces vs outside spaces")
    plt.pie(
        [desks_in_spaces, desks_outside_spaces],
        labels=["In spaces", "Outside spaces"],
        autopct="%1.1f%%",
        startangle=90,
    )
    plt.axis("equal")
    plt.savefig("A3/plot_desks_in_vs_out.png", dpi=200, bbox_inches="tight")

    # 2) Bar chart: desks in spaces per level/storey
    levels = list(desks_per_level.keys())
    counts = [desks_per_level[lvl] for lvl in levels]

    plt.figure()
    plt.bar(levels, counts)
    plt.xlabel("Level")
    plt.ylabel("Number of desks in spaces")
    plt.title("Desks in spaces per level")
    plt.savefig("A3/plot_desks_per_level.png", dpi=200, bbox_inches="tight")

    # 3) Floor area per desk distribution (< 7 m2 vs ≥ 7 ,2)
    plt.figure()
    plt.title("Floor area per desk ≤ 7 m2 vs > 7 m2")
    plt.pie(
        [desks_area_7_or_below, desks_area_above_7], 
        labels = ["< 7 m²", "≥7 m²"],
        autopct="%1.1f%%",
        startangle=90,
    )
    plt.axis("equal")
    plt.savefig("A3/plot_area_per_desk.png", dpi=200, bbox_inches="tight")

    print("Plots saved to:")
    print("  A3/plot_desks_in_vs_out.png")
    print("  A3/plot_desks_per_level.png")
    print("  A3/plot_area_per_desk.png")

make_plots()
#################### LLIST OF VARIABLES FOR FURTHERER TESTING PURPOSES ###########################    
#pattern
#list_of_ifc_files
#modelChoice
#model

#spaces
#doors
#storey

#deskSpaces
#desks_in_spaces_count
#desks_outside_spaces_count
#desks_per_level
#desks_area_above_7
#desks_area_7_or_below

#space_boxes
#space_to_doors
#door_to_space

#guidelines
#f  # file handle for output txt

#levels
#counts

#all_desks
#desks_in_spaces
#desks_without_space

#desk_name
#desk_id

#mid
#assigned_space

#settings
#################### END OF SCRIPT ###########################


