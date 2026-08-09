import argparse
import colorama
from pathlib import Path
import copy
import numpy as np
import open3d as o3d

# Blog: https://blog.csdn.net/fengbingchun/article/details/163612725

def parse_args():
	parser = argparse.ArgumentParser(description="Open3D test code")
	parser.add_argument("--task", required=True, type=str, choices=["show_point_cloud", "point_cloud_transform", "bounding_box", "down_sampling", "estimate_normals",
				"kdtree_search", "point_cloud_registration", "point_cloud_segment", "show_mesh", "mesh_base_operation", "poisson_surface_reconstruction", "3d_reconstruction"], help="specify what kind of task")
	parser.add_argument("--src_file", type=str, help="src file name")
	parser.add_argument("--dst_file", type=str, help="dst file name")

	args = parser.parse_args()
	return args

def _load_point_cloud_file(src_file):
	if src_file is None or not src_file or not Path(src_file).is_file():
		raise ValueError(colorama.Fore.RED + f"{src_file} is not a file")

	# ply_data = o3d.data.PLYPointCloud() # download fragment.ply
	pcd = o3d.io.read_point_cloud(src_file)
	if pcd.is_empty():
		raise RuntimeError(colorama.Fore.RED + f"failed to load point cloud file: {src_file}")
	return pcd

def show_point_cloud(src_file, dst_file):
	pcd = _load_point_cloud_file(src_file)

	print(f"number of points:{len(pcd.points)}; min bound:{pcd.get_min_bound()}; max bound:{pcd.get_max_bound()}; center:{pcd.get_center()}")

	# pcd.paint_uniform_color([0, 0.8, 1])

	axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0, origin=[0, 0, 0])

	o3d.visualization.draw_geometries(
		[pcd, axis],
		window_name="Open3D Point Cloud",
		# point_show_normal=True,
		width=1280,
		height=720,
		left=100,
		top=100
	)

	o3d.io.write_point_cloud(dst_file, pcd)

def _colorize(pcd, color):
    pcd.paint_uniform_color(color)
    return pcd

def _draw_with_axis(geometries, window_name):
	axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0, origin=[0, 0, 0])
	o3d.visualization.draw_geometries(geometries + [axis], window_name, width=1280, height=720)

def point_cloud_transform(src_file, dst_file):
	pcd = _load_point_cloud_file(src_file)

	pcd_origin = copy.deepcopy(pcd)
	_colorize(pcd_origin, [0.6, 0.6, 0.6]) # grey

	pcd_translate = copy.deepcopy(pcd)
	pcd_translate.translate((0.5, 0.0, 0.0))
	_colorize(pcd_translate, [1, 0, 0]) # red
	_draw_with_axis([pcd_origin, pcd_translate], "Open3D Geometry Transform: translate")

	pcd_rotate = copy.deepcopy(pcd)
	R = pcd_rotate.get_rotation_matrix_from_xyz((0, np.deg2rad(45), 0)) # Rotation matrix, rotate 45° around the Y-axis
	pcd_rotate.rotate(R, center=pcd_rotate.get_center())
	pcd_rotate.translate((0.0, 0.5, 0.0))
	_colorize(pcd_rotate, [0, 1, 0]) # green
	_draw_with_axis([pcd_origin, pcd_rotate], "Open3D Geometry Transform: rotate")

	pcd_scale = copy.deepcopy(pcd)
	pcd_scale.scale(1.5, center=pcd_scale.get_center())
	pcd_scale.translate((0.0, -0.5, 0.0))
	_colorize(pcd_scale, [0, 0, 1]) # blue
	_draw_with_axis([pcd_origin, pcd_scale], "Open3D Geometry Transform: scale")

	pcd_transform = copy.deepcopy(pcd)
	angle = np.deg2rad(30)
	T = np.array([ # 4x4 transformation matrix
		[np.cos(angle), 0, np.sin(angle), -0.5],
		[0,             1, 0,              0.0],
		[-np.sin(angle),0, np.cos(angle),  0.5],
		[0,             0, 0,              1]
	])
	pcd_transform.transform(T)
	_colorize(pcd_transform, [1, 1, 0]) # yellow
	_draw_with_axis([pcd_origin, pcd_transform], "Open3D Geometry Transform: transform")

	_draw_with_axis([pcd_origin, pcd_translate, pcd_rotate, pcd_scale, pcd_transform], "Open3D Geometry Transform")

	o3d.io.write_point_cloud(dst_file, pcd_transform)

def bounding_box(src_file):
	pcd = _load_point_cloud_file(src_file)
	# pcd.paint_uniform_color([0.6, 0.6, 0.6]) # gray

	aabb = pcd.get_axis_aligned_bounding_box()
	aabb.color = (1, 0, 0) # red
	print(f"AABB center:{aabb.get_center()}; extent:{aabb.get_extent()}; min:{aabb.get_min_bound()}; max:{aabb.get_max_bound()}")

	obb = pcd.get_oriented_bounding_box()
	obb.color = (0, 1, 0) # green
	print(f"OBB center:{obb.center}; extent:{obb.extent}; R:{obb.R}")

	axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0)
	_draw_with_axis([pcd, aabb, obb, axis], "Bounding Box Demo")

def down_sampling(src_file, dst_file):
	pcd = _load_point_cloud_file(src_file)
	print(f"original points: {len(pcd.points)}")

	# pcd_uniform_down = pcd.uniform_down_sample(every_k_points=5)
	pcd_voxel_down = pcd.voxel_down_sample(voxel_size=0.02)
	print(f"voxel down points: {len(pcd_voxel_down.points)}")

	pcd.paint_uniform_color([0.6, 0.6, 0.6])
	pcd_voxel_down.paint_uniform_color([1, 0, 0])
	pcd_voxel_down.translate((1, 1, 1))

	_draw_with_axis([pcd, pcd_voxel_down], "Voxel Down Sampling")

	o3d.io.write_point_cloud(dst_file, pcd_voxel_down)

def estimate_normals(src_file, dst_file):
	pcd = _load_point_cloud_file(src_file)
	print(f"pcd has normals: {pcd.has_normals()}")

	voxel_size = 0.02
	pcd = pcd.voxel_down_sample(voxel_size)

	pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size * 2, max_nn=30)) # KDTreeSearch
	print(f"pcd has normals: {pcd.has_normals()}; normal shape: {np.asarray(pcd.normals).shape}; normal vector of the first point(nx,ny,nz): {np.asarray(pcd.normals)[0]}")

	pcd.orient_normals_towards_camera_location(camera_location=np.array([0.0, 0.0, 0.0])) # normal orientation uniformity

	o3d.visualization.draw_geometries([pcd],  window_name="Estimate Normals", width=1280, height=720, point_show_normal=True)

	o3d.io.write_point_cloud(dst_file, pcd)

def kdtree_search(src_file, dst_file):
	pcd = _load_point_cloud_file(src_file)

	kdtree = o3d.geometry.KDTreeFlann(pcd)

	query_index = 1000
	query = pcd.points[query_index]
	[k, idx, _] = kdtree.search_knn_vector_3d(query, 100)

	colors = np.full((len(pcd.points), 3), [0.6, 0.6, 0.6])
	colors[query_index] = [1.0, 0.0, 0.0]
	colors[idx] = [0.0, 1.0, 0.0]
	colors[query_index] = [1.0, 0.0, 0.0]

	pcd.colors = o3d.utility.Vector3dVector(colors)

	_draw_with_axis([pcd], "KDTree KNN Search")

	o3d.io.write_point_cloud(dst_file, pcd)

def point_cloud_registration(src_file, dst_file):
	target = _load_point_cloud_file(src_file) # target

	source = copy.deepcopy(target) # create a source
	angle = np.deg2rad(10)
	R = np.array([
		[np.cos(angle), 0, np.sin(angle)],
		[0,             1, 0],
		[-np.sin(angle), 0, np.cos(angle)]
	])
	T = np.eye(4)
	T[:3, :3] = R
	T[:3, 3] = [0.05, 0.02, 0.03]
	source.transform(T)

	voxel_size = 0.02
	source_down = source.voxel_down_sample(voxel_size)
	target_down = target.voxel_down_sample(voxel_size)

	threshold = 0.05
	init = np.eye(4)
	result = o3d.pipelines.registration.registration_icp( # icp point cloud registration
		source_down,
		target_down,
		threshold,
		init,
		o3d.pipelines.registration.TransformationEstimationPointToPoint()
	)

	print(f"icp point cloud registration result: fitness: {result.fitness}; inlier rmse: {result.inlier_rmse}; transformation: {result.transformation}")

	source_aligned = copy.deepcopy(source)
	source_aligned.transform(result.transformation)

	target.paint_uniform_color([0.7, 0.7, 0.7])
	source.paint_uniform_color([1.0, 0.0, 0.0])
	source_aligned.paint_uniform_color([0.0, 1.0, 0.0])

	_draw_with_axis([target, source], "Before ICP")
	_draw_with_axis([target, source_aligned], "After ICP")

	o3d.io.write_point_cloud(dst_file, source_aligned)

def point_cloud_segment(src_file, dst_file):
	pcd = _load_point_cloud_file(src_file)
	print("point number:", len(pcd.points))

	plane_model, inliers = pcd.segment_plane( # ransac plane segment
		distance_threshold=0.01,
		ransac_n=3,
		num_iterations=1000
	)

	[a, b, c, d] = plane_model
	print(f"plane equation: {a:.4f}x + {b:.4f}y + {c:.4f}z + {d:.4f} = 0")
	print("plane inlier points:", len(inliers))

	plane_cloud = pcd.select_by_index(inliers)
	plane_cloud.paint_uniform_color([1, 0, 0])

	other_cloud = pcd.select_by_index(inliers, invert=True)
	other_cloud.paint_uniform_color([0.7, 0.7, 0.7])

	_draw_with_axis([plane_cloud, other_cloud], "Ransac Plane Segment")

	o3d.io.write_point_cloud(dst_file, plane_cloud)

def _load_mesh_file(src_file):
	if src_file is None or not src_file or not Path(src_file).is_file():
		raise ValueError(colorama.Fore.RED + f"{src_file} is not a file")

	mesh = o3d.io.read_triangle_mesh(src_file)
	if mesh.is_empty():
		raise RuntimeError(colorama.Fore.RED + f"failed to load mesh file: {src_file}")

	print(f"vertices number: {len(mesh.vertices)}; triangles number: {len(mesh.triangles)}")
	print(f"vertex normals number: {len(mesh.vertex_normals)}; triangle normals number: {len(mesh.triangle_normals)}")
	print(f"has vertex colors: {mesh.has_vertex_colors()}; has vertex normals: {mesh.has_vertex_normals()}; has triangle normals: {mesh.has_triangle_normals()}")
	return mesh

def show_mesh(src_file):
	mesh = _load_mesh_file(src_file)

	if not mesh.has_vertex_normals():
		mesh.compute_vertex_normals()

	_draw_with_axis([mesh], "Show Mesh")

def mesh_base_operation(dst_file):
	cube = o3d.geometry.TriangleMesh.create_box(width=1.0, height=1.0, depth=1.0)
	cube.paint_uniform_color([1.0, 0.0, 0.0])
	cube.translate([1, 0, 0])
	cube.scale(0.5, center=cube.get_center())

	sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.6, resolution=30)
	sphere.paint_uniform_color([0.0, 1.0, 0.0])
	sphere.translate([3, 0, 0])

	cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=0.5, height=1.5, resolution=30)
	cylinder.paint_uniform_color([0.0, 0.0, 1.0])
	cylinder.translate([5, 0, 0])
	R = cylinder.get_rotation_matrix_from_xyz((0, 0, np.deg2rad(45)))
	cylinder.rotate(R, center=cylinder.get_center())

	cone = o3d.geometry.TriangleMesh.create_cone(radius=0.6, height=1.5, resolution=30)
	cone.paint_uniform_color([1.0, 1.0, 0.0])
	cone.translate([7, 0, 0])

	for mesh in [cube, sphere, cylinder, cone]:
		mesh.compute_vertex_normals()
		mesh.compute_triangle_normals()

	for name, mesh in [("Cube", cube), ("Sphere", sphere), ("Cylinder", cylinder), ("Cone", cone)]:
		print(f"{name}: vertices={len(mesh.vertices)}, triangles={len(mesh.triangles)}")

	_draw_with_axis([cube, sphere, cylinder, cone], "Mesh Base Operation")

	o3d.io.write_triangle_mesh(dst_file, cone)

def poisson_surface_reconstruction(src_file, dst_file):
	pcd = _load_point_cloud_file(src_file)
	pcd.paint_uniform_color([0.8, 0.8, 0.8])
	pcd.translate([1, 0, 0])

	voxel_size = 0.02
	pcd = pcd.voxel_down_sample(voxel_size)
	pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.05, max_nn=30))
	pcd.orient_normals_consistent_tangent_plane(30)

	mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=9)

	densities = np.asarray(densities)
	threshold = np.quantile(densities, 0.05)
	vertices_to_remove = densities < threshold
	mesh.remove_vertices_by_mask(vertices_to_remove)

	mesh.compute_vertex_normals()
	mesh.translate([5, 0,0])
	mesh.paint_uniform_color([0.2, 0.7, 1.0])

	# o3d.visualization.draw_geometries([mesh], mesh_show_wireframe=True, mesh_show_back_face=True)
	_draw_with_axis([pcd, mesh], "Poisson Surface Reconstruction")

	o3d.io.write_triangle_mesh(dst_file, mesh)

def reconstruction_3d(dst_file):
	dataset = o3d.data.SampleRedwoodRGBDImages() # download open3d rgb-d datasets
	color_path = dataset.color_paths[0]
	depth_path = dataset.depth_paths[0]
	print(f"color path: {color_path}; depth path: {depth_path}")

	color = o3d.io.read_image(color_path)
	depth = o3d.io.read_image(depth_path)

	rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
		color,
		depth,
		depth_scale=1000.0,
		depth_trunc=3.0,
		convert_rgb_to_intensity=False
	)

	camera = o3d.camera.PinholeCameraIntrinsic(o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault) # camera intrinsic

	pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd, camera) # rgb-d --> point cloud
	pcd.translate([2, 0, 0])

	pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.02, max_nn=30))

	pcd.orient_normals_consistent_tangent_plane(30)

	mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8)

	densities = np.asarray(densities)
	threshold = np.quantile(densities, 0.05)
	mesh.remove_vertices_by_mask(densities < threshold)

	mesh.compute_vertex_normals()
	mesh.translate([5, 0, 0])

	_draw_with_axis([pcd, mesh], "3D Reconstruction")

	o3d.io.write_triangle_mesh(dst_file, mesh)

if __name__ == "__main__":
	colorama.init(autoreset=True)
	args = parse_args()

	if args.task == "show_point_cloud":
		show_point_cloud(args.src_file, args.dst_file)
	elif args.task == "point_cloud_transform":
		point_cloud_transform(args.src_file, args.dst_file)
	elif args.task == "bounding_box":
		bounding_box(args.src_file)
	elif args.task == "down_sampling":
		down_sampling(args.src_file, args.dst_file)
	elif args.task == "estimate_normals":
		estimate_normals(args.src_file, args.dst_file)
	elif args.task == "kdtree_search":
		kdtree_search(args.src_file, args.dst_file)
	elif args.task == "point_cloud_registration":
		point_cloud_registration(args.src_file, args.dst_file)
	elif args.task == "point_cloud_segment":
		point_cloud_segment(args.src_file, args.dst_file)
	elif args.task == "show_mesh":
		show_mesh(args.src_file)
	elif args.task == "mesh_base_operation":
		mesh_base_operation(args.dst_file)
	elif args.task == "poisson_surface_reconstruction":
		poisson_surface_reconstruction(args.src_file, args.dst_file)
	elif args.task == "3d_reconstruction":
		reconstruction_3d(args.dst_file)

	print(colorama.Fore.GREEN + "====== execution completed ======")
