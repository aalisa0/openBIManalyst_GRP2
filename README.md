# BIManalyst group 2
Group 2: s243577 & s213839

The purpose of this repo is to learn about openBIM as part of our current architectural engineering studies. 


A1: Here are 'rules' to verify if an ifc-model for no. of claimed desks and bicycle stands

See the 'A1/rules/A1_alisaRule' for code 

See the 'A1_analyst_checks_GRP2.txt' for results  



A2: The chosen use case is to verify whether the desk space in each room is compliant, using the Building2516 (ARCH-25-16-D) for our analysis.

Here we check if the the office spaces (IfcSpace) are in accordance to BR18 and 'Arbejdstilsynet' the governmental body regulating working spaces.

See the 'A2' folder for diagram of what will be analysed 




A3: Code to verify whether the desk space in each room is compliant as shown in A2, using the Building2516 (ARCH-25-16-D). 

See the 'A3/rules/A3_check_IfcSpace.py' for code and furthere down in the README

See the 'A3/A3_analyst_checks_GRP2.txt' and the diagrams for results  




A4: Video and written tutorial on how to use the code from A3
## Summary 
Title: "Checking desks in IfcSpaces"
Category: Architectural 
Description: This tutorial helps with identifying, locating, listing and verifying building elements for desks in IfcSpaces spefically. 
Using python, bonsai and ifcopenshell, and a given BIM model the code from A3 can find misplaced desks and check compliance following BR18 and 'Arbejdstilsynet' the governmental body regulating working spaces. The results are then presented in a seperate .txt file for futherer analysis. 



Written tutorial for A3 code:

Part A. What this script does
   

This script reads an IFC file and analyses desks in IfcSpaces. It does four main things:

1) Lets you pick which IFC file to use from the current folder.
2) Finds all desks in the model:
   - How many desks are inside IfcSpace objects (rooms).
   - How many desks are outside spaces (directly under storeys).
3) For each space with desks, it:
   - Finds doors belonging to that space (using door geometry).
   - Reads properties such as:
        * floor/level (from Constraints pset)
        * area and height (from Dimensions pset)
   - Calculates:
        * number of desks in the space
        * area per desk (m²)
        * volume per desk (m³)
        * total door width and door width per desk
4) Generates:
   - A text file: A3/A3_analyst_checks_GRP2.txt
   - Three plot images (PNG):
        * A pie chart: desks in spaces vs desks outside spaces
        * A bar chart: number of desks in spaces per level
        * A bar chart: number of desks where area/desk is <= 7 m² vs > 7 m²
          

Part B. Run the script

Prerequisites:
    - Python installed
    - ifcopenshell installed
    - matplotlib installed

Typical steps:
    1) Place your IFC file in the same folder as the script.
    2) Run the script (e.g. `A3/rules/A3_check_IfcSpace.py`).
    3) When prompted, type the number of the IFC file to analyse.
    4) After it finishes:
         - Open: A3/A3_analyst_checks_GRP2.txt  for the text report.
         - Open: A3/plot_desks_in_vs_out.png
                 A3/plot_desks_per_level.png
                 A3/plot_area_per_desk.png  for the plots.


Part C. Limitations 

1) Desk detection only works if the word "desk" appears in the element’s name.  
2) Desks modeled using other IFC classes than IfcBuildingElementByProxy or IfcFurniture will not be found.  
3) Doors are assigned to spaces using midpoint geometry, which can be inaccurate because of the increased margin.  
4) The script requires specific property set names (“Dimensions” and “Constraints”).  
5) The A3 folder must already exist or .txt-file saving will fail.  
6) The script cannot run 'automatically' because the user has to choose an IFC file in the beginning.  





