from PIL import Image
import imagehash
import argparse
import shelve
import glob
import sys

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,help="path to input dataset of images.")
ap.add_argument("-s", "--shelve", required=True,help="output shelve database")
ap.add_argument("-r", "--rescan", required=False,help="prompts rescan of image database if provided.",action='store_true')
ap.add_argument("-f", "--filetocompare", required=True,help="path to input file for comparison baseline.")
args = vars(ap.parse_args())
DBFilePath = args["shelve"]
IMGDirPath = args["dataset"]
Rescan = args["rescan"]
IMGPath = args["filetocompare"]

db = shelve.open(DBFilePath, writeback = True)

def fingerprintCompare(a, b):
	"""
	Compare two image hash values, return the % difference.
	https://fullstackml.com/wavelet-image-hash-in-python-3504fdd282b5
	"""
	return (a - b)/(len(a.hash)**2)

def findMatches(searchHash, db):
	"""
	Return paths and %diff as a list of tuples, to images in a database
	that match a particular fingerprint (searchHash), with a fingerprintCompare
	return value < 30%.
	"""
	return [ (x,(fingerprintCompare(searchHash, db[x]))) for x in db 
		if ( (fingerprintCompare(searchHash, db[x])) < .3 ) ]

def listFlatten(l):
	"""
	Very basic recursive function used to flatten a list.
	http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html
	
	It is NOT the best way to do this - page above covers many, many better
	algorithms. However, it is unlikely we will have more than two layers of
	recursion here, so... whatevs.
	"""
	out = []
	for item in l:
		if isinstance(item, (list, tuple)):
			out.extend(listFlatten(item))
		else:
			out.append(item)
	return out

def getImageHash(ImagePath):
	# load the image and compute the hash
	image = Image.open(ImagePath)
	return imagehash.whash(image)
	
def scanDirectory(path, db):
	"""
	Generate a fingerprint hash for the images in the provided directory, using
	wavelet hashing. Save the hashes to the database. New hashes will overwrite
	any existing hashes for files with the same path/name.
	
	https://pypi.org/project/ImageHash/
	"""
	# loop over the image dataset
	for imagePath in glob.glob(path + "/*.jpg"):
		# load the image and compute the hash
		h = getImageHash(imagePath)

		db[imagePath] = h
		print(imagePath, h)
	
	# Database is opened with writeback enabled for performance reasons. Since
	# we just did a bunch of work, now would be a good time to sync the database
	# and flush all that to disk.
	db.sync()
	
	# All done.
	return

if Rescan:
	scanDirectory(IMGDirPath, db)
	
searchHash = getImageHash(IMGPath)

for (Path, DiffPercent) in findMatches(searchHash, db):
	print(Path, "is", str(DiffPercent*100)+"%", "different than", IMGPath)
	
# close the shelf database
db.close()