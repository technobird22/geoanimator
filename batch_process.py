# Main libraries
import os
import sys
import time

# Image processing
import cv2
# import numpy as np

# Other scripts
import geocap_utils

# For logging verbose outputs to a file (progress is still output via STDERR)
# Useful for debugging. Even if set to NOT verbose, it will still output full logs to a file
VERBOSE = False

FPS = 24
FIRST_IMG = 0

INPUT_DIRECTORIES = os.listdir()
INPUT_DIRECTORIES.sort()

TARGET_DIR = "LRIT"

# Directory for a collection of every frame
EVERYTHING = "ALL_PROCESSED_FRAMES/"
IMAGE_OUTPUT_DIRECTORY = "PROCESSED_FRAMES/"

# Current directory name
DIR_NAME = os.path.basename(os.getcwd())

# Define animation output codec
FOURCC = cv2.VideoWriter_fourcc(*'mp4v')
# Dimensions for output animation (same as frame dimensions)
width = 2200 # For GK-2A frames. Todo: Add to config files
height = 2200 # For GK-2A frames. Todo: Add to config files

# Ignored directories
IGNORED_DIRS = ["config", EVERYTHING[:-1]]

# Create VideoWriter object for total animation
TOTAL_ANIMATION = cv2.VideoWriter("compilation_" + DIR_NAME + ".mp4", FOURCC, FPS, (width, height))

print(geocap_utils.VERY_BASIC_HEADER)

print("-" * 30)
print("[INFO] ---Excecution start---")

if DIR_NAME != TARGET_DIR:
    print("[WARNING] Working directory '" + DIR_NAME + "' is not the target directory. \n\
        Continue? [y/n]")
    CHOICE = input().lower()

    while(CHOICE != 'y' and CHOICE != 'n'):
        print("[ERROR] Invalid CHOICE. Please try again. Options: 'y' or 'n'")
    if CHOICE != 'y':
        print("[STATUS] Aborting...")
        exit()
else:
    print("[OK] Working directory is target directory...")

if os.path.isdir(EVERYTHING):
    print("[WARNING] Output directory '" + EVERYTHING + "' Already exists. Overwrite? [y/n]")
    CHOICE = input().lower()
    # first_dir += 1
    while(CHOICE != 'y' and CHOICE != 'n'):
        print("[ERROR] Invalid CHOICE. Please try again. Options: 'y' or 'n'")
        CHOICE = input()
    if CHOICE != 'y':
        print("[STATUS] Aborting...")
        exit()
else:
    print("[WARN] No output directory found.")
    print("[STATUS] Creating output directory...")
    try:
        os.mkdir(EVERYTHING)
    except OSError:
        print("[ERROR] Creation of the directory '" + EVERYTHING + "' failed")
    else:
        print("[OK] Successfully created the directory '" + EVERYTHING + "'.")

print("-" * 30)
print("[STATUS] ---Begin Processing---")

START_TIME = time.time()

# Try different subdirectories
print("[INFO] Directories to process: " + str(os.listdir()))
print("-"*30)
CNT = 0
for current_directory in INPUT_DIRECTORIES:
    FIRST_IMG = 0
    # Check if it is really a directory
    if not os.path.isdir(current_directory):
        print("[ERROR] Directory '" + current_directory + "' is NOT a directory! Skipping...")
        continue

    # Check if directory is being ignored
    if IGNORED_DIRS.count(current_directory) != 0:
        print("[ERROR] Directory '" + current_directory + "' is being ignored! Skipping...")
        continue

    OUTPUT_PATH = current_directory + "/" + IMAGE_OUTPUT_DIRECTORY

    if os.path.isdir(OUTPUT_PATH):
        print("[WARNING] Output directory '" + OUTPUT_PATH + "' Already exists. Overwrite?")
        # CHOICE = input()
        CHOICE = 'y'
        while(CHOICE != 'y' and CHOICE != 'n'):
            print("[ERROR] Invalid CHOICE. Please try again. Options: 'y' or 'n'")
            CHOICE = input()
        if CHOICE != 'y':
            print("[STATUS] Skipping directory...")
            continue
    else:
        print("[WARN] No output directory found.")
        print("[STATUS] Creating output directory...")
        try:
            os.mkdir(OUTPUT_PATH)
        except OSError:
            print("[ERROR] Creation of the directory '" + OUTPUT_PATH + "' failed")
        else:
            print("[OK] Successfully created the directory '" + OUTPUT_PATH + "'.")

    inputs = os.listdir(current_directory + "/FD/")[FIRST_IMG:]
    inputs.sort()
    print("[INFO] Loading inputs from directory '" + str(current_directory) + "'...")
    # print("Inputs from directory '" + str(current_directory) + "': " + str(inputs))

    CNT = 0.0

    for img_path in inputs:
        print("[STATUS] Got image: '" + str(img_path) + "'.")

    print("-" * 30)

    print(str(">"*10) + "F: " + str(FIRST_IMG))
    cur_img_path = current_directory + "/FD/" + inputs[FIRST_IMG]
    print(str(">"*10) + "F1: " + str(FIRST_IMG))

    print("[STATUS] Loading image '" + cur_img_path + "'.")
    cur_img = cv2.imread(cur_img_path)

    print("[STATUS] Getting frame dimensions...")
    height, width, c = cur_img.shape
    height, width, c = round(height), round(width), round(c)

    print("[OK] Got frame dimensions")

    print("-"*30)
    print("[INFO] VIDEO CONFIG:")
    print("Working with directory '", current_directory, "'.")
    print("Frame dimensions: ", height, " by ", width, ".")
    print("Frame rate: ", FPS, " frames per second.")

    print("Video ouput file: '", ("clahe_" + current_directory + ".mp4"), "'.")
    print("-"*30)

    # Create VideoWriter object for daily animation
    animation = cv2.VideoWriter("daily_" + current_directory + ".mp4", FOURCC, FPS, (width, height))

    if not VERBOSE:
        sys.stdout = open('debug.log', 'w')

    for relative_img_path in inputs:
        print("[INFO] Relative Path: '" + relative_img_path + "'.")
        img_path = current_directory + "/FD/" + relative_img_path
        print("[INFO] Complete Path: '" + img_path + "'.")

        # Display status
        print("[" + str(round(CNT/len(inputs)*100)) + "%] Processing image '" + img_path + \
            "'...")
        sys.stderr.write("[" + str(round(CNT/len(inputs)*100)) + "%] Processing image '"\
             + img_path + "'...\n")

        try:
            CNT += 1

            # Load image
            print("[STATUS] Loading image...")
            img = cv2.imread(img_path, 1)
            print("[OK] Loaded image.")

            # Perform CLAHE
            print("[STATUS] Performing CLAHE...")
            img = geocap_utils.clahe(img)
            print("[OK] Finished performing CLAHE.")

            # Add overlay
            print("[STATUS] Adding overlay...")
            img = geocap_utils.overlay_info(img, relative_img_path)
            time.sleep(0.1)
            print("[OK] Finished adding overlay.")

            print("[OK] Processed frame ready.")

            # Write to image
            print(">"*5 + "[INFO] '" + (OUTPUT_PATH + relative_img_path) + "' ...")
            print("[STATUS] Writing image to '" + (OUTPUT_PATH + current_directory + "_" \
                + relative_img_path) + "' ...")
            cv2.imwrite(OUTPUT_PATH + current_directory + "_" + relative_img_path, img)
            print("[OK] Successfully written image")

            # Write to EVERYTHING
            print("[STATUS] Writing image to EVERYTHING at '" \
                + (EVERYTHING + current_directory + "_" + relative_img_path) + "' ...")
            cv2.imwrite(EVERYTHING + "/" + current_directory + "_" + relative_img_path, img)
            print("[OK] Successfully written image")

            # Write to daily animation
            print("[STATUS] Writing to daily frame...")
            animation.write(img)
            print("[OK] Successfully written image to frame")

            # Write to total animation
            print("[STATUS] Writing to total frame...")
            TOTAL_ANIMATION.write(img)
            print("[OK] Successfully written image to frame")

            # If processed lots of frames, print out status
            # and wait a bit to allow the CPU to cool down
            if (CNT - 1) % 100 == 0:
                ELAPSED = round(time.time() - START_TIME, 1)
                CAL_FPS = round(ELAPSED/CNT, 4)
                ESTIMATED = round(CAL_FPS * (len(inputs) - CNT), 1)

                print("[STATUS] Time ELAPSED: " + str(ELAPSED) + " seconds. Calculation FPS: " \
                    + str(CAL_FPS) + ". ESTIMATED remaining time: " + str(ESTIMATED) + " seconds. \
                        Frame " + str(CNT) + " (" + str(round((float(CNT)/len(inputs))*100)) + "%)")

                # Pause for CPU cooloff
                if CNT >= 100:
                    print("[STATUS] Pausing 5 seconds for CPU cooloff...")
                    time.sleep(5)
        except:
            # Uh oh!
            print("[ERROR] Failed on image '" + img_path + "' with message '" \
                + str(sys.exc_info()[1]) + "'.")
            print("[STATUS] Aborting...")
            exit()

    print("[STATUS] Releasing daily animation output stream")
    try:
        animation.release()
        print("[OK] Successfully released daily animation output stream")
    except:
        print("[ERROR] Failed to release with message '" + str(sys.exc_info()[0]) + "'.\n")

    print("[INFO] --- Finished processing directory '" + current_directory + "'.---\n" + "-"*30)

print("[STATUS] Releasing total animation output stream")
try:
    TOTAL_ANIMATION.release()
    print("[OK] Successfully released total animation output stream")
except:
    print("[ERROR] Failed to release with message '" + str(sys.exc_info()[0]) + "'.\n")

print("-"*30)

if CNT == 0:
    print("[WARN] ---Did not do any processing!---")
    print("[WARN] ---Please check your working directory structure!---")
    print("[STATUS] ---Exiting...---")
    print("[STATUS] ---DONE---")
    exit()

ELAPSED = round(time.time() - START_TIME, 1)
CAL_FPS = round(CNT/ELAPSED, 4)
ESTIMATED = round(CAL_FPS * (len(inputs) - CNT), 1)
print("[STATUS] Execution finished. Total time ELAPSED: " + str(ELAPSED) + " seconds. Processed " \
    + str(CNT) + " frames. Calculation FPS: " + str(CAL_FPS) + ".")
print("[STATUS] ---DONE---")
