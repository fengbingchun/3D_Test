import argparse
import colorama
import pyvista as pv
from pyvista import examples
import numpy as np

# Blog: https://blog.csdn.net/fengbingchun/article/details/165994530

def parse_args():
	parser = argparse.ArgumentParser(description="PyVista test code")
	parser.add_argument("--task", required=True, type=str, choices=["show_sphere", "structured_grid", "image_data", "point_cloud", "bunny", "terrain_following_mesh"], help="specify what kind of task")
	parser.add_argument("--file_name", type=str, help="file name")

	args = parser.parse_args()
	return args

def show_sphere():
	sphere = pv.Sphere() # create mesh
	print(f"sphere:\n{sphere}")
	print(f"sphere.points:\n{sphere.points}")

	plotter = pv.Plotter() # create a drawing window or 3D scene
	plotter.add_mesh(sphere) # add mesh to the scene
	plotter.show()

def structured_grid():
	height_matrix = np.random.rand(50, 100) * 10
	h, w = height_matrix.shape

	x = np.arange(w, dtype=np.float64)
	y = np.arange(h, dtype=np.float64)
	xx, yy = np.meshgrid(x, y)

	grid = pv.StructuredGrid(xx, yy, height_matrix) # create a structured mesh
	grid["height"] = height_matrix.ravel()
	print(f"grid array names: {grid.array_names}")
	# grid.plot()

	plotter = pv.Plotter()
	plotter.add_mesh(grid, scalars="height", cmap="jet") # scalars=height_matrix.ravel()
	plotter.add_axes()
	plotter.show_grid()
	plotter.show()

def image_data():
	data = np.random.rand(30, 50, 50)

	grid = pv.ImageData(dimensions=(50, 50, 30), spacing=(1.0, 1.0, 2.0), origin=(0.0, 0.0, 0.0))
	grid["values"] = data.ravel(order="F")
	grid.plot(scalars="values", cmap="jet")

def point_cloud():
	rng = np.random.default_rng(seed=0)
	points = rng.random((100, 3))
	mesh = pv.PolyData(points)
	mesh.plot(point_size=10, style="points")

def bunny():
	mesh = examples.download_bunny_coarse()

	pl = pv.Plotter()
	pl.add_mesh(mesh, show_edges=True, color="white")
	pl.add_points(mesh.points, color="red", point_size=2)
	pl.camera_position = pv.CameraPosition(position=(0.1, 0.5, 1.0), focal_point=(0.02, 0.03, -0.022), viewup=(0, 1, 0)) # precisely configure camera(observer) parameters in a 3D scene
	pl.show()

def terrain_following_mesh(file_name):
	# save vtk file
	# dem = examples.download_crater_topo()
	# dem.save("crater_topo.vtk")

	# load vtk file
	dem = pv.read(file_name)
	# dem.plot(show_edges=False, cmap="terrain")

	terrain = dem.warp_by_scalar()
	# terrain.plot()

	z_cells = np.array([25] * 5 + [35] * 3 + [50] * 2 + [75, 100])

	xx = np.repeat(terrain.x, len(z_cells), axis=-1)
	yy = np.repeat(terrain.y, len(z_cells), axis=-1)
	zz = np.repeat(terrain.z, len(z_cells), axis=-1) - np.cumsum(z_cells).reshape((1, 1, -1))

	mesh = pv.StructuredGrid(xx, yy, zz)
	mesh["Elevation"] = zz.ravel(order="F")

	cpos = pv.CameraPosition(position=(1825925.1133451513, 5638088.652334543, 6338.62406077208), focal_point=(1821066.0, 5649249.0, 943.0), viewup=(-0.3311592878804317, 0.2899315569977654, 0.8979271787329846)) # the value is obtained from plotter.camera_position
	# mesh.plot(show_edges=True, lighting=False, cpos=cpos)
	# print(f"Camera: position: {mesh.camera_position}") # 'StructuredGrid' object has no attribute 'camera_position'

	plotter = pv.Plotter()
	plotter.add_mesh(mesh, show_edges=True, lighting=False)
	plotter.camera_position = cpos
	plotter.show()
	print(f"camera position(position, focal_point, viewup): \n{plotter.camera_position}")

if __name__ == "__main__":
	colorama.init(autoreset=True)
	args = parse_args()

	# import inspect
	# print(f"python file name: {inspect.getfile(pv.Plotter)}")

	if args.task == "show_sphere":
		show_sphere()
	elif args.task == "structured_grid":
		structured_grid()
	elif args.task == "image_data":
		image_data()
	elif args.task == "point_cloud":
		point_cloud()
	elif args.task == "bunny":
		bunny()
	elif args.task == "terrain_following_mesh":
		terrain_following_mesh(args.file_name)

	print(colorama.Fore.GREEN + "====== execution completed ======")
