# Практическое задание "Анализатор прайс-листов."
import os
import pandas as pd


class PriceMachine():
    def __init__(self):
        self.data = pd.DataFrame()
        self.list_files_ = []
        self.file_path = ''

    def load_prices(self, file_path=''):
        '''
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар, название, наименование, продукт
            Допустимые названия для столбца с ценой:
                розница, цена
            Допустимые названия для столбца с весом (в кг.)
                вес, масса, фасовка
        '''
        self.file_path = file_path
        # ищем имена файлов с прайсами
        for root, dirs, files in os.walk(self.file_path):
            for file in files:
                if file.endswith('.csv') and 'price' in file:
                    self.list_files_.append(file)
        if len(self.list_files_) == 0:  # если файлов нет выходим
            print('Файлы прайс-листов не найдены')
            return False
        print('обнаружены файлы прайс-листов')
        _ = [print(file) for file in self.list_files_]
        # читаем данные из каждого файла и помещаем в датафрейм
        for filename in self.list_files_:
            df = pd.read_csv(file_path + filename, encoding='UTF-8', delimiter=',')
            # переименовываем столбцы под один шаблон
            df.rename(columns={'название': 'Product',
                               'продукт': 'Product',
                               'товар': 'Product',
                               'наименование': 'Product',
                               'цена': 'Price',
                               'розница': 'Price',
                               'фасовка': 'Wght',
                               'масса': 'Wght',
                               'вес': 'Wght'
                               }, inplace=True)
            # указываем из какого файла запись
            df['File'] = filename
            # оставляем только нужные столбцы
            df = df[['Product', 'Price', 'Wght', 'File']]
            # создаем столбец с ценой за килограмм
            df['Prc_kg'] = round(df['Price'] / df['Wght'], ndigits=2)
            # добавляем прайс к общему прайс-листу
            self.data = pd.concat([self.data, df], ignore_index=True)
        # отсортируем по возрастанию цены за кг
        self.data = self.data.sort_values('Prc_kg', ascending=True, ignore_index=True)
        print(' файлы прочитаны, вся информация занесена в общий прайс-лист, отсортирована')
        print(self.data)
        return True

    def export_to_html(self, fname='output.html'):
        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
        '''
        pd.set_option('display.max_colwidth', None)
        # переименуем столбцы на русский
        data_frame = self.data.rename(columns={'Product': 'Название',
                                               'Price': 'Цена',
                                               'Wght': 'Фасовка',
                                               'File': 'Файл',
                                               'Prc_kg': 'Цена за кг.',
                                               })
        table_html = data_frame.to_html()
        footer = '''
        </body>
        </html>
        '''
        fname = self.file_path + fname
        with open(fname, 'w', encoding='utf-8') as file:
            file.write(result + table_html + footer)
            file.close()
        pass

    def find_text(self, text):
        '''
        ищем продукты в датафрейме содержащие в названии text
        '''
        print('-------------------------- РЕЗУЛЬТАТ ЗАПРОСА ---------------------------')
        # отбираем строки где в названии продукта есть text
        resultat = self.data.loc[self.data.apply(lambda x: text.lower() in x['Product'].lower(), axis=1)]
        if len(resultat) > 0:
            with pd.option_context('display.max_rows', None, 'display.max_columns', 7, 'display.max_colwidth', 40):
                print(resultat.sort_values('Prc_kg', ascending=True, ignore_index=True))
        else:
            print('Ничего не найдено')
        print('------------------------------------------------------------------------')

        pass


'''
    Логика работы программы
'''
pm = PriceMachine()
while True:
    file_path = input('Укажите путь к папке с файлами прайс-листов >')
    if not os.path.exists(file_path):
        print(f'Путь {file_path} не найден')
        continue  # возвращаемся к выбору папки
    if pm.load_prices(file_path=file_path):
        # если файлы есть и прочитаны продолжаем работу
        while True:
            enter = input('\nУкажите часть названия продукта или exit для выхода >')
            if enter.lower() == 'exit':
                break
            pm.find_text(text=enter)
        print('the end - работа анализатора завершена')
        # узнаем надо ли сохранить html после завершения
        while True:
            html_name = input(
                '\nДля сохранения общего прайса в HTML, задайте имя файла, \nесли имя пустое файл не будет создан >')
            html_name = str(html_name)
            if len(html_name) != 0:
                if not '.html' in html_name and not '.htm' in html_name:
                    html_name = html_name + '.html'
                try:
                    pm.export_to_html(fname=html_name)
                    print(f'Файл {html_name} сохранен')
                    break
                except:
                    print(f'Неверное имя {html_name}, файл не создан')
                    continue
            break
    else:
        continue
    break
print('Программа завершена')
