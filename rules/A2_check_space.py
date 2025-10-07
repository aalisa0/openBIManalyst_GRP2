#I want to check if the desks in office spaces 
import ifcopenshell as ifc
import ifcopenshell.util.classification
import ifcopenshell.util.selector

#Load your IFC file
ifc_path = '/Users/alisatellefsen/Library/CloudStorage/OneDrive-DanmarksTekniskeUniversitet/DTU/Kandidat/2. Sem/41934 Advanced BIM/openBIManalyst_GRP2/25-16-D-ARCH.ifc'
model = ifc.open(ifc_path)

spaces = model.by_type("IfcSpace")

def is_desk(element):
    if element.is_a("IfcBuildingElementProxy") or element.is_a("IfcFIfcFurniture"):
        name = (element.Name or "").lower()
        obj_type = (element.ObjectType or "").lower()
        return "desk" in name or "desk" in obj_type
    return False

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
    #else:
        #print("  → No desks found.")


psets = ifcopenshell.util.element.get_psets(spaces[0])
print(psets['Dimensions'])


with open("A2_analyst_checks_GRP2.txt", "w") as f:
  f.write("I have analysed desks in the office spaces in the ifc model.\n")
  f.write("I have done so in accordance to 'Arbejdstilsynet' the governmental body regulating working spaces.\n")
 