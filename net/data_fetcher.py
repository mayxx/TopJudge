import os
import json
import torch
from word2vec import word2vec

transformer = word2vec()

unk = torch.randn(200)
unk = unk / torch.norm(unk)
unk = unk.numpy()
pad = torch.randn(200)
pad = pad / torch.norm(pad)
pad = pad.numpy()

def get_num_classes(s):
    if s == "crit":
        return 3
    if s == "law":
        return 4
    if s == "time":
        return 14
    gg


def get_data_list(d):
    return d.replace(" ", "").split(",")


def analyze_crit(data, config):
    return data[0]


def analyze_law(data, config):
    pass


def analyze_time(data, config):
    # print(data)
    # gg
    if data["sixing"]:
        return 0
    if data["wuqi"]:
        return 1
    v = 0
    for x in data["youqi"]:
        v = max(x, v)
    for x in data["juyi"]:
        v = max(x, v)
    for x in data["guanzhi"]:
        v = max(x, v)
    if v > 25 * 12:
        return 2
    if v > 15 * 12:
        return 3
    if v > 10 * 12:
        return 4
    if v > 7 * 12:
        return 5
    if v > 5 * 12:
        return 6
    if v > 3 * 12:
        return 7
    if v > 2 * 12:
        return 8
    if v > 1 * 12:
        return 9
    if v > 9:
        return 10
    if v > 6:
        return 11
    if v > 0:
        return 12
    return 13


word_dict = {}


def get_word_vec(x, config):
    #if not (x in word_dict):
    #    word_dict[x] = torch.rand(config.getint("data", "vec_size"))
    vec = transformer.load(x)
    #print(type(vec))
    if vec is None:
        return unk,True
    else:
        return vec,True

    #return word_dict[x], True


def generate_vector(data, config):
    data = data.split("\t")
    vec = []
    for x in data:
        y, z = get_word_vec(x, config)
        #print(y,z)
        if z:
            vec.append(torch.from_numpy(y))
    len_vec = len(vec)
    while len(vec) < config.getint("data", "pad_length"):
        #vec.append(torch.zeros(config.getint("data", "vec_size")))
        vec.append(torch.from_numpy(pad))
   
    #print(torch.stack(vec))
    return torch.stack([torch.stack(vec)]), len_vec


def parse(data, config):
    label_list = config.get("data", "type_of_label").replace(" ", "").split(",")
    label = []
    for x in label_list:
        if x == "crit":
            label.append(analyze_crit(data["meta"]["crit"], config))
        if x == "law":
            label.append(analyze_law(data["meta"]["law"], config))
        if x == "time":
            label.append(analyze_time(data["meta"]["time"], config))
    vector, len_vec = generate_vector(data["content"], config)
    return vector, len_vec, torch.LongTensor(label)


def check(data, config):
    if len(data["meta"]["crit"]) > 1:
        return False
    #if len(data["meta"]["law"]) > 1:
    #    return False

    return True


def create_dataset(file_list, config):
    dataset = []
    for file_name in file_list:
        file_path = os.path.join(config.get("data", "data_path"), str(file_name))
        if not(os.path.isfile(file_path)):
            continue
        print("Loading data from " + file_name + ".")
        cnt = 0
        f = open(file_path, "r")
        for line in f:
            data = json.loads(line)
            if check(data, config):
                if cnt % 10000 == 0:
                    print("Already load " + str(cnt) + " data...")
                dataset.append(parse(data, config))
                cnt += 1
        f.close()
        print("Loading " + str(cnt) + " data from " + file_name + " end.")

    return dataset#DataLoader(dataset, batch_size=config.getint("data", "batch_size"),
             #         shuffle=config.getboolean("data", "shuffle"), drop_last=True, num_workers=4)


def init_train_dataset(config):
    return create_dataset(get_data_list(config.get("data", "train_data")), config)


def init_test_dataset(config):
    return create_dataset(get_data_list(config.get("data", "test_data")), config)


def init_dataset(config):
    train_dataset = init_train_dataset(config)
    test_dataset = init_test_dataset(config)

    return train_dataset, test_dataset
