"""
Make train, val, test datasets based on train_test_split.txt, and by sampling val_ratio of the official train data to make a validation set 
Each dataset is a list of metadata, each includes official image id, full image path, class label, attribute labels, attribute certainty scores, and attribute labels calibrated for uncertainty
"""
import os
import random
import pickle
import argparse
from os import listdir
from os.path import isfile, isdir, join
from collections import defaultdict as ddict


def extract_data(data_dir):
    cwd = os.getcwd()
    data_path = join(cwd,data_dir + 'images')
    val_ratio = 0.2

    path_to_id_map = dict() #map from full image path to image id
    with open(data_path.replace('images', 'images.txt'), 'r') as f:
        for line in f:
            items = line.strip().split()
            path_to_id_map[join(data_path, items[1].replace('/', '\\'))] = int(items[0])


    is_train_test = dict() #map from image id to 0 / 1 (1 = train)
    with open(join(cwd, data_dir + 'train_test_split.txt'), 'r') as f:
        for line in f:
            idx, is_train = line.strip().split()
            is_train_test[int(idx)] = int(is_train)
    print("Number of train images from official train test split:", sum(list(is_train_test.values())))

    val_files = None

    train_val_data, test_data = [], []
    train_data, val_data = [], []
    folder_list = [f for f in listdir(data_path) if isdir(join(data_path, f))]
    folder_list.sort() #sort by class index
    for i, folder in enumerate(folder_list):
        folder_path = join(data_path, folder)
        classfile_list = [cf for cf in listdir(folder_path) if (isfile(join(folder_path,cf)) and cf[0] != '.')]
        #classfile_list.sort()
        for cf in classfile_list:
            img_id = path_to_id_map[join(folder_path, cf)]
            img_path = join(folder_path, cf)
            metadata = {'id': img_id, 'img_path': img_path, 'class_label': i}
            if is_train_test[img_id]:
                train_val_data.append(metadata)
                if val_files is not None:
                    if img_path in val_files:
                        val_data.append(metadata)
                    else:
                        train_data.append(metadata)
            else:
                test_data.append(metadata)

    random.shuffle(train_val_data)
    split = int(val_ratio * len(train_val_data))
    train_data = train_val_data[split :]
    val_data = train_val_data[: split]
    print('Size of train set:', len(train_data))
    return train_data, val_data, test_data



data_dir=""
save_dir=os.getcwd()

train_data, val_data, test_data = extract_data(data_dir)

for dataset in ['train','val','test']:
    print("Processing %s set" % dataset)
    f = open(join(save_dir, dataset + '.pkl'), 'wb')
    if 'train' in dataset:
        pickle.dump(train_data, f)
    elif 'val' in dataset:
        pickle.dump(val_data, f)
    else:
        pickle.dump(test_data, f)
    f.close()

