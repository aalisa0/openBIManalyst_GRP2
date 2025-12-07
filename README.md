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

## A5: Reflections

See 'A5' folder for the same text. 

The tool I developed is a desk-checking tool based on criteria from ‘Arbejdstilsynet’, the Danish regulatory authority for workplace environments.
The use case we created in A2 was admittedly chosen in a bit of a panic. Still, despite that, the tool ultimately works quite well and checks exactly what I intended it to.
However, the code has become very specific to this particular model. Instead of functioning as a universal desk-finding tool for any possible IFC model, it only works reliably with this one (25-16-D-ARCH.ifc), which is unfortunate.
There are several uncertainties. For example, the margin of the bounding box is set to 0,5 m, but if another door is close by and not actually an exit, the tool might misidentify it. It’s also necessary to be careful with bounding boxes, bbox, in general, as a flat virtual square can appear as a diamond depending on its orientation however I use it in a 3D dimension ‘IfcSpace’, so that should not be a problem, but for father studies I will try to remember that. 
Many of the limitations comes from the model itself as well as the structure of my code. I wish I had designed the code with more interchangeable variables, for instance, to check chairs or windows, so it could be reused more flexibly.
That said, the tool is very useful in the B-stage and for iterating or counting desks throughout the project.
As for openBIM, I originally expected it to play only a small role in my academic future. However, after the guest lecture about two weeks ago, I am now certain that in my career, at some point, will be connected to openBIM.

Group reflections:
The GitHub collaboration was a less integrated which is a shame because I think I will definitely use it in the future. 


## Written tutorial for A3 code:


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





