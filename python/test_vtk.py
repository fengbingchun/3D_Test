import vtk
import colorama
import argparse

# Blog: https://blog.csdn.net/fengbingchun/article/details/163994311

def parse_args():
	parser = argparse.ArgumentParser(description="VTK test code")
	parser.add_argument("--task", required=True, type=str, choices=["show_rectangle", "show_cuboid"], help="specify what kind of task")

	args = parser.parse_args()
	return args

def show_rectangle():
	# create 4 points
	points = vtk.vtkPoints()
	points.InsertNextPoint(0.0, 0.0, 0.0)
	points.InsertNextPoint(10.0, 0.0, 0.0)
	points.InsertNextPoint(10.0, 5.0, 0.0)
	points.InsertNextPoint(0.0, 5.0, 0.0)

	# create a quadrilateral
	quad = vtk.vtkQuad()
	quad.GetPointIds().SetId(0, 0)
	quad.GetPointIds().SetId(1, 1)
	quad.GetPointIds().SetId(2, 2)
	quad.GetPointIds().SetId(3, 3)

	# create PolyData
	cells = vtk.vtkCellArray()
	cells.InsertNextCell(quad)

	poly_data = vtk.vtkPolyData()
	poly_data.SetPoints(points)
	poly_data.SetPolys(cells)

	# Mapper
	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputData(poly_data)

	# Actor
	actor = vtk.vtkActor()
	actor.SetMapper(mapper)

	# Renderer
	renderer = vtk.vtkRenderer()
	renderer.AddActor(actor)
	renderer.SetBackground(0.1, 0.2, 0.3)

	# RenderWindow
	render_window = vtk.vtkRenderWindow()
	render_window.AddRenderer(renderer)
	render_window.SetSize(800, 600)

	# Interactor
	interactor = vtk.vtkRenderWindowInteractor()
	interactor.SetRenderWindow(render_window)

	# show
	renderer.ResetCamera()
	render_window.Render()

	interactor.Start()

def show_cuboid():
	# create a cuboid
	cube = vtk.vtkCubeSource()
	cube.SetXLength(10.0)
	cube.SetYLength(5.0)
	cube.SetZLength(3.0)

	# Mapper
	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputConnection(cube.GetOutputPort())

	# Actor
	actor = vtk.vtkActor()
	actor.SetMapper(mapper)
	actor.GetProperty().SetColor(0.2, 0.8, 0.3)
	actor.GetProperty().EdgeVisibilityOn()
	actor.GetProperty().SetEdgeColor(1.0, 1.0, 1.0)

	# Renderer
	renderer = vtk.vtkRenderer()
	renderer.AddActor(actor)
	renderer.SetBackground(0.1, 0.1, 0.1)

	# Render Window
	render_window = vtk.vtkRenderWindow()
	render_window.AddRenderer(renderer)
	render_window.SetSize(800, 600)

	# Interactor
	interactor = vtk.vtkRenderWindowInteractor()
	interactor.SetRenderWindow(render_window)

	# show
	renderer.ResetCamera()
	render_window.Render()

	interactor.Start()

if __name__ == "__main__":
	colorama.init(autoreset=True)
	args = parse_args()

	if args.task == "show_rectangle":
		show_rectangle()
	elif args.task == "show_cuboid":
		show_cuboid()

	print(colorama.Fore.GREEN + "====== execution completed ======")
