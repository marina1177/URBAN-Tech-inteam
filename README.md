Плагин ОСУ ОДС "Гос Услуги" (Beta) - Проект создан как сервис для оптимизации расходов на санитарное содержание улиц.
 
## Введение

Для определения характерных участков со снежным покровом таких как:

- Локальные сугробы 
- Снежные валы

Решено применять совместную систему из широкоугольной камеры со светофильтром ИК диапазона, 2 лазера ИК диапазона 905 нм с цилиндрической линзой для построения прямых линий для повышения точности распознавания неровностей на дорожном полотне. Выбор именной такой частоты обусловлен безопасностью для людей и животных, лазер такой частоты применяется в автомобильных лидарах.

Предполагается установка камеры на верхней части кузова сзади автомобиля осуществляющего сгребание, погрузку или контроль за состоянием ОДХ.
Камера устанавливается с углом наклона 60 градусов, лазеры - 30 градусов к плоскости дороги. Такое взаимное расположение повышает точность определения высоты объектов. Второй лазер позволяет судить о форме объекта.

![2019-12-01 22 40 45](https://user-images.githubusercontent.com/49564849/69919427-ab978680-148d-11ea-824d-3c0d7b8e1fe9.jpg)

Исходя из принятых характеристик камеры с полем зрения в горизонтальной плоскости 90 градусов и высоты установки около 2.5 м достигается отрисовка линии и её анализ на ширине порядка 15 м. Предполагая использование камеры с соотношением сторон изображения 16:9 ожидаемый вертикальный угол обзора ~51 градус. Учитывая разрешение матрицы 1920х1080 точек, смещение линии, построенной лазером, на изображении на 1 пиксель дает 2.2 мм смещения на плоскости. В реальных условиях ожидаемая точность достаточна для определения формы и размера объектов из снега на дорожном покрытии и оценки качества уборки прилегающих к бордюрам зон дороги.

![suBHkBp0K-8](https://user-images.githubusercontent.com/49564849/69920190-e998a880-1495-11ea-9f45-087c725ecba2.jpg)

![BglwtuT9ddI](https://user-images.githubusercontent.com/49564849/69920195-f4533d80-1495-11ea-9765-877102fac7cf.jpg)

## Развитие функционала

На протяжении всей деятельности проекта велась работа по развитию и расширению его функционала, решение масштабируется от одного округа до целого города и  страны в целом.

Рализованный на данный момент функционал:

- Рабочее дополнение существующей городской системы автоматизации в части учета новых факторов оценки уборочных операций в зимнее время (локальных - по камерам, линейных по модулям на транспорте).
- Учет уровня прав пользователя при авторизации на сайте (контрактор, подрядчик, гражданин).
- Интерактивная карта с отображением статистики качества по треку движения уборочной техники (% качества) и локальных зон (% качества по доступу к видеокамерам городской сети), статистика по зоне ответственности компаний.

## Планируемый функционал

- Учет существующих данных для построения зон ответственности, обработки телеметрии, обращений граждан, учета выполняемых операций и планов уборки для оценки и учета в алгоритмах.
- Использование технологии контейнеризации и Kubernetes для горизонтального масштабирования позволяет оперативно развернуть решение на серверах и масштабировать их мощность пропорционально покрываемой зоне учета.

## Результат который мы получилил

![1d2753fb-d4f5-48a5-8204-5ee22fdcf794](https://user-images.githubusercontent.com/49564849/69919518-9ff88f80-148e-11ea-9248-b2b4524b88e6.gif)

```
import sys
import cv2 as cv
import numpy as np
import matplotlib.path as mpltPath


def shape_detection(x, y, dots_array):
    point = [y, x]
    path = mpltPath.Path([dots_array[0][0], dots_array[0][1], dots_array[0][2], dots_array[0][3]])
    return(path.contains_point(point))

def four_point_transform(image, pts):
    rect = np.array([
		pts[0][0],
		pts[0][1],
		pts[0][2],
		pts[0][3]], dtype = "float32")
    tl = pts[0][0]
    tr = pts[0][1]
    br = pts[0][2]
    bl = pts[0][3]
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
    M = cv.getPerspectiveTransform(rect, dst)
    warped = cv.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def dots_coloring(image, array_ref):
    for dot in array_ref:
        cv.circle(image, (dot[0],dot[1]), 5, (0, 255, 0), thickness=1, lineType=8, shift=0)
    return(image)

def click_and_crop(event, x, y, flags, param):
    global array_ref, cropping
    if event == cv.EVENT_LBUTTONUP and cropping == False:
        array_ref.append((x, y))

def blue_blur_count_trapeze(dots_array):
    global blue_basic, blur_basic,backup, color, path

    backup = cv.imread(path)
    blue, red, gree = cv.split(backup)
    image_hsv = cv.cvtColor(backup, cv.COLOR_BGR2HLS)

    hue,lum, sat = cv.split(image_hsv)
    blur = cv.GaussianBlur(hue,(5,5),0)
    min_x = min(dots_array[0][0][1],
                dots_array[0][1][1],
                dots_array[0][2][1],
                dots_array[0][3][1])
    min_y = min(dots_array[0][0][0],
                dots_array[0][1][0],
                dots_array[0][2][0],
                dots_array[0][3][0])
    max_x = max(dots_array[0][0][1],
                dots_array[0][1][1],
                dots_array[0][2][1],
                dots_array[0][3][1])
    max_y = max(dots_array[0][0][0],
                dots_array[0][1][0],
                dots_array[0][2][0],
                dots_array[0][3][0])
    first_triangle = (dots_array[0][0],
                        dots_array[0][2],
                        np.array([dots_array[0][0][0], dots_array[0][2][1]], dtype=np.int32))
    second_triangle = (dots_array[0][1],
                        dots_array[0][3],
                        np.array([dots_array[0][1][0], dots_array[0][3][1]], dtype=np.int32))
    backup_y = min_y
    #cv.circle(backup, (first_triangle[0][0],first_triangle[0][1]), 5, (40, 255, 20), thickness=10, lineType=8, shift=0)
    #cv.circle(backup, (first_triangle[1][0],first_triangle[1][1]), 5, (40, 255, 20), thickness=10, lineType=8, shift=0)
    #cv.circle(backup, (first_triangle[2][0],first_triangle[2][1]), 5, (40, 255, 20), thickness=10, lineType=8, shift=0)
    while (min_x < max_x):
        while (min_y < max_y):
            if (shape_detection(min_x, min_y, dots_array) == True):
                if (blur[min_x][min_y] > blur_basic):
                    if (blue[min_x][min_y] > blue_basic):
                        backup[min_x][min_y] = color
            min_y = min_y + 1
        min_y = backup_y
        min_x = min_x + 1
    return(backup)

def blue_blur_count(backup):
    blue, red, gree = cv.split(backup)
    image_hsv = cv.cvtColor(backup, cv.COLOR_BGR2HLS)

    hue,lum, sat = cv.split(image_hsv)
    blur = cv.GaussianBlur(hue,(5,5),0)
    x = 0
    y = 0
    while (x < len(blur)):
        while (y < len(blur[x])):
            if blur[x][y] > blur_basic:
                if blue[x][y] > blue_basic:
                    backup[x][y] = [0,255,255]
            y = y + 1
        y = 0
        x = x + 1
    return(backup)

path = "/Users/s.korotkov/666/sonia.jpg"
color = [0,255,255]
blur_basic = 15
blue_basic = 120
array_ref = []
cropping = False
image = cv.imread(path)
backup = cv.imread(path)
while True:
    backup = dots_coloring(backup, array_ref)
    if len(array_ref) == 4:
        cropping = True
    else:
        cv.setMouseCallback("wow", click_and_crop)
    cv.imshow("wow", backup)
    if cropping == True:
        #cv.createTrackbar("blue", "wow", blue_basic, 255, setBlueBasic)
        #cv.createTrackbar("hue", "wow", blur_basic, 255, setBlurBasic)
        if array_ref[0][0] > array_ref[1][0]:
            temp = array_ref[0]
            array_ref[0] = array_ref[1]
            array_ref[1] = temp
        if array_ref[2][0] < array_ref[3][0]:
            temp = array_ref[2]
            array_ref[2] = array_ref[3]
            array_ref[3] = temp
        a3 = np.array( [[array_ref[0],array_ref[1],array_ref[2],array_ref[3]]], dtype=np.int32 )
        warped = four_point_transform(image, a3)
        blue_blur_count_trapeze(a3)
        cv.imshow("warped", warped)
        cv.line(backup, array_ref[0], array_ref[1], (0, 0, 255), 5, 8, 0)
        cv.line(backup, array_ref[1], array_ref[2], (0, 0, 255), 5, 8, 0)
        cv.line(backup, array_ref[2], array_ref[3], (0, 0, 255), 5, 8, 0)
        cv.line(backup, array_ref[3], array_ref[0], (0, 0, 255), 5, 8, 0)
        #cv.fillPoly(backup, a3, 255)
    if cv.waitKey(25) & 0xFF == ord('q'):
        break
cv.destroyAllWindows()
```
http://git2.urbantech.pro/inteam/ut_inteam_project/tree/snow_detection

## Built With

* [Python/OPEN.CV/matplotlib/numpy](https://www.python.org/)
* [JavaScript](https://www.javascript.com/)
* [HTML/CSS]()
* [D3.js]()
* [Jango]()
* [Docker](https://www.docker.com/)
* [postgreSQL]()


## Authors

* **Dobroklonskaya M.**  - [marina.d](https://github.com/marina1177)
* **Lukyanova S.** - [sonya.l](https://github.com/ilovetostudyit)
* **Voyteskiy S.** - [sergey.v](https://github.com/rbednar-vs)
* **Korotkov S.** - [sergey.k](https://github.com/therealadespina)
* **Gulyaev S.** - [semen.g](https://github.com/devsagul/)
