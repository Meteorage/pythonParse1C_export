#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import re
import sys
# from sys import argv
from datetime import datetime

path_source = sys.argv[1]
path_destination = sys.argv[2]
dict_reverse_dir = dict()
dict_ignore_dir = dict()
list_all_files = []


class FileDescription:

    def __init__(self, path_file, path_local_file, method_call, name_proc, text_proc):
        self.path_file = path_file
        self.path_local_file = path_local_file
        self.method_call = method_call
        self.name_proc = name_proc
        self.text_proc = text_proc
        self.array = []

    def update_path_local_file(self):
        self.update_name_proc()
        local_path = self.path_file
        for rev in dict_reverse_dir.keys():
            local_path = local_path.replace(rev, dict_reverse_dir.get(rev))
        local_path = local_path.replace(path_source, '')
        local_path = local_path.replace('\\\\', '\\')
        local_path = local_path.replace('\\', '/')
        self.path_local_file = local_path
        temp_method_call = local_path + '/' + self.name_proc
        if temp_method_call.find('Общие модули') > 0:
            temp_method_call = temp_method_call.replace('Общие модули', '')
        temp_method_call = temp_method_call.replace('/', '.')
        temp_method_call = temp_method_call.replace('..', '.')
        if temp_method_call[0] == '.':
            temp_method_call = temp_method_call[-len(temp_method_call) + 1:]
        if temp_method_call[len(temp_method_call) - 1] == '.':
            temp_method_call = temp_method_call[:len(temp_method_call) - 1]
        self.method_call = temp_method_call
        self.analysis_of_called_methods()

    def update_name_proc(self):
        temp = self.name_proc
        temp = re.sub(r'\(.*', '', temp)
        self.name_proc = temp.strip()

    def delete_duplicates(self):
        n = []
        for i in self.array:
            if i not in n:
                n.append(i)
        self.array = n

    def analysis_of_called_methods(self):
        sample = re.compile(r"(([a-zA-Z0-9_а-яА-Я]+)\.|)([a-zA-Z0-9_а-яА-Я]+)\.([a-zA-Z0-9_а-яА-Я]+)\((?:.|\n)*?", re.U)
        list_block_of_call = sample.findall(self.text_proc)
        for item in list_block_of_call:
            temp_call = ""
            for part_call in item:
                if len(part_call.strip()) == 0:
                    continue
                else:
                    if len(temp_call) > 0:
                        temp_call = temp_call + '.' + part_call
                    else:
                        temp_call = part_call
            temp_call = temp_call.replace('(', '')
            self.array.append(temp_call)
        self.delete_duplicates()


def init():
    dict_reverse_dir["AccumulationRegisters"] = 'Регистры накопления'
    dict_reverse_dir["InformationRegisters"] = 'Регистры сведений'
    dict_reverse_dir["CommonModules"] = 'Общие модули'
    dict_reverse_dir["Documents"] = "Документы"
    dict_reverse_dir["Catalogs"] = "Справочники"
    dict_reverse_dir["DocumentJournals"] = "Журнал документов"
    dict_reverse_dir["Ext"] = ""
    dict_reverse_dir["Forms"] = ""
    dict_reverse_dir["ManagerModule.bsl"] = ""
    dict_reverse_dir["ObjectModule.bsl"] = ""
    dict_reverse_dir["Templates"] = ""
    dict_reverse_dir["DataProcessors"] = "Обработки"
    dict_reverse_dir["Module.bsl"] = ""

    # игнорирование папок
    dict_ignore_dir["Commands"] = ''
    dict_ignore_dir["SettingsStorages"] = ''
    dict_ignore_dir["Forms"] = ''
    dict_ignore_dir["Help"] = ''
    dict_ignore_dir["DocumentNumerators"] = ''
    dict_ignore_dir["DocumentNumerators"] = ''
    dict_ignore_dir["DocumentNumerators"] = ''
    dict_ignore_dir["XDTOPackages"] = ''
    dict_ignore_dir["WSReferences"] = ''
    dict_ignore_dir["Reports"] = ''
    dict_ignore_dir["CommonPictures"] = ''
    dict_ignore_dir["CommonTemplates"] = ''
    dict_ignore_dir["Constants"] = ''
    dict_ignore_dir["Tasks"] = ''
    dict_ignore_dir["DefinedTypes"] = ''
    dict_ignore_dir["EventSubscriptions"] = ''
    dict_ignore_dir["FunctionalOptions"] = ''
    dict_ignore_dir["Roles"] = ''
    dict_ignore_dir["SessionParameters"] = ''
    dict_ignore_dir["SettingsStorages"] = ''
    dict_ignore_dir["StyleItems"] = ''
    dict_ignore_dir["Subsystems"] = ''
    dict_ignore_dir["CommandGroups"] = ''
    dict_ignore_dir["ChartsOfCharacteristicTypes"] = ''
    dict_ignore_dir["Common"] = ''
    dict_ignore_dir["CommonCommands"] = ''
    dict_ignore_dir["BusinessProcesses"] = ''


def parse_file(path):
    list_text = []

    if path[-4:] == '.xml':
        return
    # file_obj = codecs.open(path, "r", "utf-8-bom", 'ignore')
    with open(path, 'r', encoding='utf-8') as file:
        try:
            lines = file.readlines()
        except UnicodeDecodeError:
            lines = []
    for item_file in lines:
        lines_file = re.sub(r'//.*', '', item_file)
        lines_file = lines_file.strip()
        if len(lines_file) <= 1:
            continue
        if lines_file[0] == '#' or lines_file[0] == '|':
            continue
        list_text.append(lines_file)

    full_text = '\n'.join(list_text)
    full_text = full_text.replace('  ', ' ')
    sample = re.compile(r"(процедура|функция)((?:.|\n)*?)экспорт((?:.|\n)*?)конец(процедуры|функции)", re.IGNORECASE)
    list_block = sample.findall(full_text)
    for item_list_block in list_block:
        desc = FileDescription(path, '', item_list_block[1], item_list_block[1], item_list_block[2])
        desc.update_path_local_file()
        if desc.method_call.find('\n') == -1:
            list_all_files.append(desc)


def scan_dir(path):
    for i in os.listdir(path):
        if os.path.isdir(path + '\\' + i):
            if dict_ignore_dir.get(i) is None:
                scan_dir(path + '\\' + i)
        else:
            parse_file(path + '\\' + i)


def create_files_first_step():
    for item_description in list_all_files:

        delta_path = path_destination
        array_path = item_description.path_local_file.split('/')
        for i in range(0, len(array_path)):
            if len(array_path[i]) == 0:
                continue
            delta_path = delta_path + '\\' + array_path[i]
            if not os.path.isdir(delta_path):
                os.mkdir(delta_path)
        temp_name_file = item_description.method_call.replace('.', ' ')
        new_path = delta_path + '\\' + temp_name_file + '.md'

        is_error = 0
        with (open(new_path, 'w+', encoding='utf-8') as f):
            tag = item_description.path_local_file[-len(item_description.path_local_file) + 1:]
            tag = tag.replace('/', '_')
            tag = tag.replace(' ', '_')
            f.writelines('#' + tag + '\n')
            for item_call in item_description.array:
                if is_error == 1:
                    break
                for item_description_all in list_all_files:
                    if item_call == item_description_all.method_call:
                        local_link = item_description_all.path_local_file[
                                     -len(item_description_all.path_local_file) + 1:]
                        local_link = local_link + item_description_all.method_call.replace('.', ' ')
                        local_link = local_link + '|' + item_description_all.name_proc
                        f.writelines('[[' + local_link + ']]\n')
            f.writelines('\n')


if __name__ == '__main__':
    new_datetime = datetime.now()
    init()
    scan_dir(path_source)
    create_files_first_step()
    current_time = datetime.now()
    delta = current_time - new_datetime
    print(delta)
