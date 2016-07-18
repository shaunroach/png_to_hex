png_to_hex
=====

Turns a png file into a json file that describes a set of hex tiles whose color is the most prominent color of the hex area of the png file input.

Run the script like: python png_to_hex.py -img near_london.png -out out.json

The json is an array of elements like this: [{"i": 0, "j": 0, "pixel": [151, 151, 151]}, {"i": 0, "j": 1, "pixel": [151, 151, 151]}]
where i and j are the x,y coords of the hex tile and pixel is an rgb array of the tile's color.

Will add a viewer for the json output soon.
