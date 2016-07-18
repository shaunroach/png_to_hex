import png
import math
import json
import sys

class Grid:
    def __init__(self, width, height, line_length):
        self.width = width
        self.height = height
        self.line_length = line_length
        
        self.offset_top = 0
        self.offset_left = 0
        
        self.top_x_offset = self.line_length*math.cos(math.pi/6)
        self.top_y_offset = self.line_length*math.sin(math.pi/6)
        self.grid_space = 2*self.top_x_offset

        self.max_x = math.ceil(self.width/self.grid_space)
        self.max_y = math.ceil(self.height/(self.line_length+self.top_y_offset))
        self.x_start = 0
        self.y_start = 0
        
    def translate_coordinates_to_cell(self, x, y):
        ix_y = math.floor(y/(self.line_length+self.top_y_offset))
        adj_x = x-((ix_y)%2)*self.top_x_offset
        ix_x = math.floor(adj_x/self.grid_space)

        rem_y = y - (ix_y*(self.line_length+self.top_y_offset))
        rem_x = adj_x - (ix_x*self.grid_space)
        
        if( rem_y > self.line_length ):
            if( rem_x < self.top_x_offset ):
                ratio = (rem_y - self.line_length)/rem_x
                line_ratio = self.top_y_offset/self.top_x_offset
                if( ratio > line_ratio ):
                    ix_x -= 1
                    ix_y += 1
            else:
                ratio = (-rem_y + self.line_length + self.top_y_offset)/(rem_x - self.top_x_offset)
                line_ratio = self.top_y_offset/self.top_x_offset
                if( ratio < line_ratio ):
                    ix_y += 1

        coords = {"x": int(ix_x), "y": int(ix_y)}
        #print(coords)
    
    def get_coord_of_cell(self,x,y):
        x_cell_start = self.x_start + x*self.grid_space + ( (y%2)*self.top_x_offset)
        y_cell_start = self.y_start + y*(self.line_length + self.top_y_offset)
        
        cell_coords = []
        
        cell_coords.append({ "x":x_cell_start, "y":y_cell_start })
        cell_coords.append({ "x":x_cell_start+self.top_x_offset, "y":y_cell_start - self.top_y_offset })
        cell_coords.append({ "x":x_cell_start+self.grid_space, "y":y_cell_start })
        cell_coords.append({ "x":x_cell_start+self.grid_space, "y": y_cell_start + self.line_length })
        cell_coords.append({ "x":x_cell_start+self.top_x_offset, "y": y_cell_start + self.line_length+self.top_y_offset })
        cell_coords.append({ "x": x_cell_start, "y": y_cell_start + self.line_length })
        
        return cell_coords

def get_pixel_at(x,y, pixels, pixel_byte_width, row_width, grid):
    pixel_position = int(x + y*row_width)
    pixel_x = pixel_position*pixel_byte_width
    pixel_y = (pixel_position+1)*pixel_byte_width
    pixel = pixels[int(pixel_x): int(pixel_y)]
    grid.translate_coordinates_to_cell(x,y)
    return pixel
    
def get_most_frequent_pixel(coords, pixels, pixel_byte_width, row_width, grid):
    colors = {}
    for coord in coords:
        coord_color = get_pixel_at(coord["x"],coord["y"], pixels, pixel_byte_width, row_width, grid)
        if( len(coord_color) != 3 ):
            coord_arr = [0,120,0]
        else:
            coord_arr = [coord_color[0], coord_color[1], coord_color[2]]
        key = str(coord_arr[0])+","+str(coord_arr[1])+","+str(coord_arr[2])
        if not key in colors.keys():
            colors[key] = {"count": 0, "pixel": coord_arr}
        colors[key]["count"] += 1
        
    common_pixel = None
    top_count = 0
    for key in colors.keys():
        if( colors[key]["count"] > top_count ):
            top_count = colors[key]["count"]
            common_pixel = colors[key]["pixel"]
    
    return common_pixel
    
def parse_options(args):
    ret_dict = {}
    for i in range(0,len(args),2):
        assert( (i+1) < len(args) )
        param = args[i]
        val = args[i+1]
        
        ret_dict[param] = val
        
    #set default val of hexsize
    if( not "-hexsize" in ret_dict.keys() ):
        ret_dict["-hexsize"] = 6
    
    return ret_dict

if __name__ == "__main__":

    param_dict = parse_options(sys.argv[1:])
    assert( "-img" in param_dict.keys() )
    assert( "-out" in param_dict.keys() )
    
    input_image = param_dict["-img"]
    output_json = param_dict["-out"]
    hex_size = int(param_dict["-hexsize"])
    
    r = png.Reader(input_image)
    w, h, pixels, metadata = r.read_flat()
    grid = Grid(w,h,hex_size)
    pixel_byte_width = 4 if metadata['alpha'] else 3
    new_pixel_value = (255, 0, 0, 0) if metadata['alpha'] else (255, 0, 0)
    
    
    out_arr = []
    for i in range(0,int(grid.max_x)):
        for j in range(0,int(grid.max_y)):
            coords = grid.get_coord_of_cell(i,j)
            pixel = get_most_frequent_pixel(coords, pixels, pixel_byte_width, w, grid)
            out_vals = {"i": i, "j": j, "pixel": pixel}
            out_arr.append(out_vals)
            #print(out_vals)
   

    out_str = json.dumps(out_arr)
    
    f = file(output_json,"w")
    f.write(out_str)
    f.close()
    
    
    
