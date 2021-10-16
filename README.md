# Recosys 2.0
Вторая версия моего проекта рекомендательной системы, основанной на содержимом. Может рекомендовать игры, аниме, фильмы.

## Описание
Данный проект предназначен для личных целей. Очередной кусок говнокода, который никому не нужен, кроме меня. Собственно, таковым он задумывался с самого начала. 
Это, как уже было сказано выше, — рекомендательная система, основанная на содержимом объектов. Изначально я хотел создать модель классификации как рекомендательную систему, но что-то (мне в голову пришла замечательная идея - а почему бы, после того, как подготовка данных уже была завершена, не сделать свой набор данных по играм?) пошло не так и, в итоге, я взял тот же подход, что и год назад, в [этом](https://github.com/Vephral/Recosys) проекте. Основное отличие данного проекта от прошлого - почти весь код был написан мной, отсюда и такое низкое качество.

Так-с, теперь о самой рекомендательной системе. Все, что нужно о ней знать - то, что я решил взять объекты с их признаками и вычислить между ними схожесть. Всё. Вся рекомендательная система. Однако, большое внимание было уделено данным, поэтому рекомендации такой простой системы меня устраивают. Рекомендации можно вывести как в консоли, так и в сообщениях группы в ВК. Взял я этот подход, так как ни на что больше не хватило ~фантазии~ сил.

Я не знаю, кто это будет читать, но лучше прямо сейчас уйти, так как дальше - куча гавна.

## Описание файлов
На самом деле, вы бы не разобрались во всем этом без меня. Уверяю вас. (нет)
С папкой `datasets` все понятно. `draft_notebooks` - папка с Jupyter Notebook, в которых содержится более объемная информация по разным частям кода, а ещё говнокод, что не был задействован в проекте. Внутри этой папки есть ещё одна папка - `crutch` - что с буржуйского переводится как "костыль". Это действительно костыль, так как из-за того, что у меня не удалось задействовать многопоточность в Jupyter, мне пришлось её имитировать, создав несколько одинаковых ноутбуков. В других файлах находится обычный код (вау).

## Некоторые уточнения
Так как уже сам задолбался с этим проектом, то никакой поддержки осуществляться не будет.

Проблем много. Как например, большое потребление памяти - примерно 12 гб - при вызове рекомендаций для игр, из чего следует, что меньше чем 32 гб оперативной памяти для запуска данного типа рекомендаций не подойдет. 

Также, из-за того, что я не хочу, чтобы пользователи подолгу ждали исполнения кода, я сделал мнимую подготовку данных. Нет, она делается, но для рекомендаций используются созданные заранее матрицы для вычисления их схожести. Multiprocessing, как я не пытался, не заработал. 

Для того чтобы получить рекомендации в ВК, нужно несколько раз запустить рекомендательную систему. Это упрощенно, если по шагам, то: сначала, дождаться, пока пользователь напишет команду, затем, если команда закончилась, запустить систему снова, а потом ждать рекомендаций... Звучит легко, но, на самом деле, придется постараться, чтобы получить рекомендацию, из-за того, что могут возникнуть проблемы вроде устаревания особенного числа, нужного для того, чтобы пометить событие, где событие - ВСЕ, что делает пользователь.

# Ссылки на источники
Для начала, ссылки на наборы данных:
- [TMDB 5000 Movie Dataset](https://www.kaggle.com/tmdb/tmdb-movie-metadata)
- [Anime Recommendation Database](https://www.kaggle.com/hernan4444/anime-recommendation-database-2020)
- [IGDB](https://www.igdb.com/discover) - ссылка на сайт, так как я сам собирал данные через их API.

Те, что не были использованы в конечной версии, но использовались на ранних этапах:
- [Steam Store Games (Clean dataset)](https://www.kaggle.com/nikdavis/steam-store-games)
- [Video Game Sales Data](https://www.kaggle.com/holmjason2/videogamedata)
- [Video Game Sales](https://www.kaggle.com/gregorut/videogamesales)

Применение метода Bag-of-Words вдохновлялся (нагло сворован) отсюда:
- [03_classification.ipynb](https://github.com/ageron/handson-ml2/blob/master/03_classification.ipynb)