#include "VTK_Test.h"
#include <QApplication>
#include <QVTKOpenGLNativeWidget.h>

#include <vtkActor.h>
#include <vtkNew.h>
#include <vtkNamedColors.h>
#include <vtkPolyDataMapper.h>
#include <vtkProperty.h>
#include <vtkRenderer.h>
#include <vtkRenderWindow.h>
#include <vtkCubeSource.h>
#include <vtkGenericOpenGLRenderWindow.h>

// Blog: https://blog.csdn.net/fengbingchun/article/details/163994311

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    VTK_Test window;
    window.resize(1000, 700);

    auto* vtkWidget = new QVTKOpenGLNativeWidget(&window);
    window.setCentralWidget(vtkWidget);

    vtkNew<vtkGenericOpenGLRenderWindow> renderWindow;
    vtkWidget->setRenderWindow(renderWindow);

    vtkNew<vtkRenderer> renderer;
    renderWindow->AddRenderer(renderer);

    vtkNew<vtkCubeSource> cube;

    vtkNew<vtkPolyDataMapper> mapper;
    mapper->SetInputConnection(cube->GetOutputPort());

    vtkNew<vtkActor> actor;
    actor->SetMapper(mapper);

    renderer->AddActor(actor);
    renderer->ResetCamera();

    renderWindow->Render();

    window.show();

    return app.exec();
}
