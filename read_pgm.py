import numpy as np
import matplotlib.pyplot as plt


def map_to_world_frames(mx, my, resolution, map_offset, map_originX, map_originY):
    wx = map_originX + (mx+map_offset)*resolution
    wy = map_originY + (my+map_offset)*resolution
    return wx, wy

def world_to_map(wx, wy, map_originX, map_originY, resolution, map_height, map_width):
    if (wx < map_originX or wy < map_originY):
        raise Exception("World coordinates out of bounds")

    mx = int((wx - map_originX) / resolution)
    my = int((wy - map_originY) / resolution)
    
    if  (my > map_height or mx > map_width):
        raise Exception("Out of bounds")

    return (mx, my)
    
def read_pgm(pgm_fp):
    with open(pgm_fp, 'rb') as pgm_file:
        # Read magic number
        magic_number = pgm_file.readline().strip()
        assert magic_number == b'P5', f"Expected 'P5', but got '{magic_number}'"
        
        # Read width, height, and max gray value
        dimensions_line = pgm_file.readline().strip()
        while dimensions_line.startswith(b'#'):  # Skip comments
            dimensions_line = pgm_file.readline().strip()
        
        width, height = map(int, dimensions_line.split())
        max_gray = int(pgm_file.readline().strip())
        
        # Read pixel data
        pixel_data = np.frombuffer(pgm_file.read(), dtype=np.uint8)
        
        return (pixel_data, (height, width), max_gray)



data = read_pgm(r'C:\Users\labee\path_planning\map\playground.pgm')
image_data = np.reshape(data[0], data[1])

map_height, map_width = image_data.shape # map cell sizes
print(f"map height: {map_height}, map_width: {map_width}")

origin_x, origin_y = world_to_map(0,0, -10.3, -10.5, 0.05, map_height, map_width)
print(f"origin_map_coordinates: {origin_x, origin_y}")
plt.figure()
cmap = plt.cm.gray
cmap.set_bad(color='red')
plt.imshow(image_data, cmap=cmap, vmin=0, vmax=255)
plt.title("PGM Map Data")
plt.plot(origin_x, origin_y, 'rx')
plt.show()

# dimensions of the pgm map image


cell_resolution = 0.05 # [m/cell]
x_coords = np.zeros_like(image_data, dtype=float)
y_coords = np.zeros_like(image_data, dtype=float)

for my in range(map_height):
    for mx in range(map_width):
        x_coords[my, mx], y_coords[my, mx] = map_to_world_frames(mx, my, cell_resolution, 0.0, -10.3, -10.5)


# finding the obstacle coordinates
occupied_thresh = 0.65
free_thresh = 0.25
count=0
data_dic = {}
for row_data in image_data:
    for data in row_data:
        if data in data_dic:
            data_dic[data]+=1
        else:
            data_dic[data]=1

print(data_dic)

free_spaces_world = []
outside_spaces_world = []
obstacle_spaces_world = []
for my in range(map_height):
    for mx in range(map_width):
        pixel_point = image_data[my, mx]
        if pixel_point == 254:
            wx, wy = map_to_world_frames(mx, my, cell_resolution, 0.0, -10.3, -10.5)
            free_spaces_world.append((wx, wy))
        elif pixel_point == 205:
            wx, wy = map_to_world_frames(mx, my, cell_resolution, 0.0, -10.3, -10.5)
            outside_spaces_world.append((wx, wy))
        elif pixel_point == 0:
            wx, wy = map_to_world_frames(mx, my, cell_resolution, 0.0, -10.3, -10.5)
            obstacle_spaces_world.append((wx, wy))


        
free_map_coords = [world_to_map(wx, wy, -10.3, -10.5, cell_resolution, map_height, map_width) for wx, wy in free_spaces_world]
free_mx_coords = [coord[0] for coord in free_map_coords]
free_my_coords = [coord[1] for coord in free_map_coords]

outside_map_coords = [world_to_map(wx, wy, -10.3, -10.5, cell_resolution, map_height, map_width) for wx, wy in outside_spaces_world]
outside_mx_coords = [coord[0] for coord in outside_map_coords]
outside_my_coords = [coord[1] for coord in outside_map_coords]

obstacle_map_coords = [world_to_map(wx, wy, -10.3, -10.5, cell_resolution, map_height, map_width) for wx, wy in obstacle_spaces_world]
obstacle_mx_coords = [coord[0] for coord in obstacle_map_coords]
obstacle_my_coords = [coord[1] for coord in obstacle_map_coords]

plt.figure()
cmap = plt.cm.gray
cmap.set_bad(color='red')
plt.imshow(image_data, cmap=cmap, vmin=0, vmax=255)
#plt.scatter([msx], [msy], color='red')  # Plot the selected point in red
plt.scatter(free_mx_coords, free_my_coords, color='blue', s=1)  # Plot the free spaces in blue
#plt.scatter(outside_mx_coords, outside_my_coords, color='red', s=1)  # Plot the outside spaces in red
plt.scatter(obstacle_mx_coords, obstacle_my_coords, color='green', s=1)  # Plot the obstacle spaces in red
plt.title("PGM Map Data")
plt.show()

