#I want to check if the desks in office spaces 
import ifcopenshell as ifc
import ifcopenshell.util.classification
import ifcopenshell.util.selector
import re, os

pattern = r".*\.ifc$"  # Match all files ending with ".ifc"

list_of_ifc_files = []

cnt = 1

for filename in os.listdir("."):
    if re.search(pattern, filename):
        print(str(cnt)+".", filename)
        list_of_ifc_files.append(filename)
        cnt += 1

modelChoice = int(input("\nWhich ifc file do you want to use? (Please enter the number corresponding to the file):\n"))

#Load IFC file
model = ifc.open(list_of_ifc_files[modelChoice - 1])

spaces = model.by_type("IfcSpace")

#Function to identify if an element is a desk
def is_desk(element):
    if element.is_a("IfcBuildingElementProxy") or element.is_a("IfcFIfcFurniture"):
        name = (element.Name or "").lower()
        obj_type = (element.ObjectType or "").lower()
        return "desk" in name or "desk" in obj_type
    return False
#List to store spaces with desks
deskSpaces = []
#Iterate through spaces and check for desks and print quantity
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
        deskSpaces.append(space)
    else:
        print("  → No desks found.")

#Quantities are found in the property sets ('psets') of the spaces
psets = ifcopenshell.util.element.get_psets(spaces[0])
print(psets['Dimensions'])

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
        psets = ifcopenshell.util.element.get_psets(space)
        
        #Findes no. of desks iin space
        desks_in_space = []
        for rel in model.get_inverse(space):
            if rel.is_a("IfcRelContainedInSpatialStructure"):
                for element in rel.RelatedElements:
                    if is_desk(element):
                        desks_in_space.append(element)

        
        if 'Dimensions' in psets:
            dimensions = psets['Dimensions']
            height = dimensions.get('Unbounded Height', 'N/A')
            floor_area = dimensions.get('Area', 'N/A')
            floor_area_desk = floor_area / len(desks_in_space)
            volume_per_desk = (height * floor_area_desk)
            #Here we find the desk dimensions, however there is no length property in the pset
            #There is a desk length in the name of the element though
            desk_length = dimensions.get('Length', 'N/A')

            f.write(f"  - Height: {round(height*pow(10, -3),2)} m\n")
            f.write(f"  - Area: {round(floor_area,2)} m2\n")
            f.write(f"  - Volume per desk: {round(volume_per_desk* pow(10, -3), 2)} m3\n")
            f.write(f"  - Area per desk: {round(floor_area_desk,2)} m2\n")
            f.write(f"  - Length of desk: {desk_length} mm\n")

        else:
            f.write("  - No Dimensions Pset found.\n")




