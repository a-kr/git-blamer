﻿Git-blamer
===========

Программа извлекает из Git-репозитория данные о развитии проекта и визуализирует их.

Что оно умеет
--------------

Извлекается следующая информация:

 * граф коммитов;
 * данные об авторстве (число строк по git blame) для каждого (текстового) файла и каждой ревизии.
   * есть возможность фильтрации по типам файлов; более хитрой обработки пока нет (т.е. пустые строки не игнорируются, например).
 
По массиву данных об авторстве строятся графики изменения объема проекта в целом и вклада (как абсолютного, так и относительного) отдельных авторов проекта во времени. Файловый браузер позволяет увидеть данные об авторстве для целых каталогов и отдельных файлов.

Результаты работы сохраняются пока только в виде статической HTML-страницы, пары картинок и пары JS-файлов с данными.

Что оно еще не умеет
---------------------
 * объединять разные имена одного автора;
 * считать более сложные метрики, чем число строк по git blame;
 * рисовать более красивые картинки или анимацию;
 * принимать маски имен файлов и прочие настройки как параметры (пока это все задано в коде).

Зависимости: библиотека PIL.
