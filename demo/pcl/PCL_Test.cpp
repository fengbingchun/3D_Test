#include <iostream>
#include <cmath>

#include <pcl/point_types.h>
#include <pcl/point_cloud.h>
#include <pcl/visualization/pcl_visualizer.h>

// Blog: https://blog.csdn.net/fengbingchun/article/details/167175942

int main()
{
    pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZRGB>);

    for (float x = -5.0f; x <= 5.0f; x += 0.1f) {
        for (float y = -5.0f; y <= 5.0f; y += 0.1f) {
            const float r = std::sqrt(x * x + y * y);

            pcl::PointXYZRGB point{};
            point.x = x;
            point.y = y;
            point.z = std::sin(r);

            const float z = point.z;
            point.r = static_cast<std::uint8_t>((z + 1.0f) * 127.5f);
            point.g = 100;
            point.b = static_cast<std::uint8_t>((1.0f - z) * 127.5f);

            cloud->push_back(point);
        }
    }

    pcl::visualization::PCLVisualizer viewer("PCL XYZRGB Viewer");
    viewer.setBackgroundColor(0.1, 0.1, 0.1);
    viewer.addPointCloud<pcl::PointXYZRGB>(cloud, "cloud");
    viewer.setPointCloudRenderingProperties(pcl::visualization::PCL_VISUALIZER_POINT_SIZE, 3, "cloud");
    viewer.addCoordinateSystem(1.0);

    while (!viewer.wasStopped()) {
        viewer.spinOnce(10);
    }

    return 0;
}

