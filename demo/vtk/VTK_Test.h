#pragma once

#include <QMainWindow>
#include "ui_VTK_Test.h"

class VTK_Test : public QMainWindow
{
    Q_OBJECT

public:
    VTK_Test(QWidget *parent = nullptr);
    ~VTK_Test();

private:
    Ui::VTK_TestClass ui;
};
