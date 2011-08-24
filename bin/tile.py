#!/usr/bin/python
#
# Copyright (c) 2011 Soichi Hayashi (https://sites.google.com/site/soichih/)
# Licensed under the MIT License 
#
# TileViewer HTML5 server-side script
# Version: 2.0.0
#
# Dependency:
#
#     You need to install GraphicsMagick (http://www.graphicsmagick.org/)
#     > yum install GraphicsMagick
#
# Usage
# ./tile.py <source_image> <output_dir>

import os
import sys
import subprocess
import time


#configuration
source_image = sys.argv[1]
tile_dir = sys.argv[2]
tmpdir="/usr/local/tmpdir"
tilesize=256

basename = os.path.basename(source_image)
os.putenv("MAGICK_TMPDIR", tmpdir)

#is this a fits file?
#if not source_image.endswith(".fits"):
#    print source_image,"is not a fits file"
#    sys.exit(1)

#if tile directory already exist, skip this image
if os.path.exists(tile_dir):
    print tile_dir,"already exists .. bailing"
    sys.exit(1)

#print time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
print "generating tile for", source_image
os.makedirs(tile_dir)

#repeatedly reduce the image size
level=0
processing_image = source_image 
while 1:
    print "level", level
    level_dir = tile_dir+"/level"+str(level)
    os.makedirs(level_dir)
    cmd = "gm convert "+processing_image+" -crop "+str(tilesize)+"x"+str(tilesize)+" "+level_dir+"/%d.png"
    print cmd
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in proc.stdout.readlines():
        print line.strip()
    #proc.stdout.close()
    if proc.wait() != 0:    
        print "ERROR : while runing $ "+cmd
        for line in proc.stderr.readlines():
            print line.strip()
        sys.exit(1)

    #if number of images are lower than it should, we are done
    count = 0
    for root, dirs, files in os.walk(level_dir):
        for file in files:    
            count += 1
    if count == 1:
        break

    #create new level
    level=level+1

    #shrink
    dest_image = tmpdir + "/" + "tile.level" + str(level) + "." + os.path.basename(basename)
    #cmd = "gm convert "+processing_image+" -resize 50% "+dest_image
    cmd = "gm convert "+processing_image+" -scale 50% "+dest_image
    print cmd
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in proc.stdout.readlines():
        print line.strip()

    #proc.stdout.close()
    if proc.wait() != 0:    
        print "ERROR : while runing $ "+cmd
        for line in proc.stderr.readlines():
            print line.strip()
        sys.exit(1)


    #remove previously used temp file (if exist)
    if level > 1:
        os.remove(processing_image)

    processing_image = dest_image

print "creating thumnail from last processing image"
cmd = "gm convert "+processing_image+" -normalize -size 128x128 -resize 128x128 +profile \"*\" "+tile_dir+"/thumb.png"
proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
for line in proc.stdout.readlines():
    print line.strip()

print "creating info.json"
cmd = "gm identify "+source_image
prop = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
lines = prop.stdout.readlines();
size = lines[0].split(" ")[2].split("+")[0].split("x")
info = open(tile_dir + "/info.json", "w")
info.write("{\n")
info.write("\"width\": "+size[0]+",\n")
info.write("\"height\": "+size[1]+",\n")
info.write("\"tilesize\": "+str(tilesize)+"\n")
info.write("}")

#remove last used tmp file
if level > 1:
    os.remove(processing_image)

print "all done"

