import os
from PIL import Image
import argparse
import pandas as pd

parser = argparse.ArgumentParser(description='Creates a TTS deck of cards.')

parser.add_argument(
	"--directory",
	type=str,
	help="The directory where the deck files are located.",
	default=".",
)
parser.add_argument(
	"--deck-name",
	type=str,
	help="The file to name the deck.",
	default="deck.png",
)
parser.add_argument(
	"--deck-back",
	type=str,
	help="The filepath to the back of the deck.",
	default=None,
)
parser.add_argument(
	"--deck-width",
	type=int,
	help="The width of the TTS deck.",
	default=9,
)
parser.add_argument(
	"--deck-height",
	type=int,
	help="The height of the TTS deck.",
	default=4,
)
parser.add_argument(
	"--deck-data",
	type=str,
	help="The order of technologies to be placed in the deck.",
	default="tech_tree.csv"
)
parser.add_argument(
	"--file-extension",
	type=str,
	help="The file extension for the files in the tech_order.txt",
	default=".jpeg"
)
    
args = parser.parse_args()

directory = args.directory

filenames = os.listdir(directory)

filenames.sort()
# Read the CSV file
df = pd.read_csv(args.deck_data)

# Get the file names from the "Technology Names" field
deck_order = df["Technology Name"].tolist()

# Remove any /'s in the file names
deck_order = [
    name.replace("/", "")+args.file_extension for name in deck_order
]

image_paths = []
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith(args.file_extension) and file in deck_order:
            image_paths.append(os.path.join(root, file))

images = []
for d in deck_order:
    for path in image_paths:
        if d in path:
            images.append(Image.open(path))
            break
    

c = 0

imgs = []


for i in range(args.deck_height):
    imgs.append([])
    for j in range(args.deck_width):
        if c >= len(filenames):
            break
        imgs[i].append(images[c])
        c += 1

width, height = imgs[0][0].size

total_width = width * args.deck_width
total_height = height * args.deck_height

deck = Image.new('RGB', (total_width, total_height))

c = 0
for i in range(args.deck_height):
    for j in range(args.deck_width):
        if c >= len(images):
            break

        deck.paste(images[c], (j*width, i*height))
        c += 1
  
if args.deck_back is not None:      
    deck.paste(
        Image.open(args.deck_back),
        (total_width - width, total_height - height)
    )

deck.save(args.deck_name)
    

front_print_folder = os.path.join(args.directory+"/Generic", "Front Print Bleeds")
front_print_images = []
for file in os.listdir(front_print_folder):
    if file.endswith(".png"):
        image_path = os.path.join(front_print_folder, file)
        front_print_images.append(Image.open(image_path))


# The CSV File has a Technology Type field. 
# Use that field to paste each technology image in the images
# list to place it centered on each front_print_images entry in a new 
# list as there will be some overlap.
# If the technology type is propulsion that corresponds to b
# If the technology type is Biotic that corresponds to g
# If the technology type is Cybernetic that corresponds to y
# If the technology type is Warfare that corresponds to r
# Then the number of prereqs in any of the "B Prereqs", "Y Prereqs", "G Prereqs", or "R Prereqs"
# Corresponds to the number.
# Then append .png
# This means a Propulsion technology with 3 in Y Prereqs should be
# Pasted centered on the image named b3.png in the Front Print Bleeds
# Folder 

front_print_images_with_tech = []
count = 0

research_icon_path = os.path.join(args.directory, "research_icon.png")
research_icon = Image.open(research_icon_path)

output_directory = os.path.join(args.directory+"/Generic", "generatedPrintBleedFronts")
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

for tech_type, prereq_b, prereq_y, prereq_g, prereq_r in zip(df["Technology Type"], df["B Prereqs"], df["Y Prereqs"], df["G Prereqs"], df["R Prereqs"]):
    tech_image_name = None
    prereq = 0
    if pd.notnull(prereq_b):
        prereq += prereq_b
    elif pd.notnull(prereq_y):
        prereq += prereq_y
    elif pd.notnull(prereq_g):
        prereq += prereq_g
    elif pd.notnull(prereq_r):
        prereq += prereq_r

    prereq = int(prereq)

    if tech_type == "Propulsion":
        tech_image_name = "b" + str(prereq) + ".png"
    elif tech_type == "Biotic":
        tech_image_name = "g" + str(prereq) + ".png"
    elif tech_type == "Cybernetic":
        tech_image_name = "y" + str(prereq) + ".png"
    elif tech_type == "Warfare":
        tech_image_name = "r" + str(prereq) + ".png"
    if tech_image_name is not None:
        tech_image_path = os.path.join(front_print_folder, tech_image_name)
        tech_image = Image.open(tech_image_path)
        front_print_images_with_tech.append(tech_image)
        x = (front_print_images_with_tech[count].width - images[count].width) // 2
        y = (front_print_images_with_tech[count].height - images[count].height) // 2
        front_print_images_with_tech[count].paste(
            images[count],
            (x, y),
            mask=images[count].convert("RGBA").split()[-1]
        )
        x = images[count].width - 25
        y = (front_print_images_with_tech[count].height - images[count].height) // 2 + 25
        front_print_images_with_tech[count].paste(
            research_icon,
            (x, y),
            mask=research_icon.convert("RGBA").split()[-1]
        )
        front_print_images_with_tech[count].save(os.path.join(
            output_directory,
            tech_image_name[:-4]+" "+deck_order[count][:-len(args.file_extension)] + ".png"
        ))

        count += 1

