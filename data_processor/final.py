# coding: UTF-8

import os
import json
import thulac
import re

cutter = thulac.thulac(model_path=r"/home/zhx/models", seg_only=True, filt=False)

in_path = "/disk/mysql/law_data/classified_data/刑事判决书"
out_path = "/disk/mysql/law_data/final_data2/"
mid_text = u"\t"
title_list = ["docId", "caseNumber", "caseName", "spcx", "court", "time", "caseType", "bgkly", "yuanwen", "document",
              "cause", "docType", "keyword", "lawyer", "punishment", "result", "judge"]

min_length = 32
max_length = 1024

accusation_file = "/home/zhx/law_pre/data_processor/accusation_list2.txt"
f = open(accusation_file, "r")
accusation_list = json.loads(f.readline())
for a in range(0, len(accusation_list)):
    accusation_list[a] = accusation_list[a].replace('[', '').replace(']', '')
f.close()

accusation_regex = ""
for x in accusation_list:
    if len(accusation_regex) != 0:
        accusation_regex += "|"
    accusation_regex += x

accusation_regex = r"(被告人){0,1}(\S{2,3}?(、([^、]{2,3}?))*)(犯){0,1}(非法){0,1}(" + accusation_regex + ")"
print(accusation_regex)
accusation_regex = re.compile(accusation_regex)

num_process = 1
num_file = 20


def cut(s):
    data = cutter.cut(s)
    result = ""
    first = True
    for x, y in data:
        if x == " ":
            continue
        if first:
            first = False
        else:
            result = result + mid_text
        result = result + x
    return result


def format_string(s):
    return s.replace("b", "").replace("\t", " ").replace("t", "")


def parse_criminals(data):
    se = set()
    """if "DSRXX" in data["document"]:
        s = format_string(data["document"]["DSRXX"])
        regex = re.compile(r"被告人((自报|：|,)?)(\S{2,4}?)[，。、,.（\(]")
        se = set()

        for result in re.finditer(regex, s):
            se.add(result.group(3))

    if not ("DSRXX" in data["document"]) or len(se) == 0:
        s = format_string(data["document"]["content"])
        regex = re.compile(r"被告人((自报|：|，)?)(\S{2,4}?)[，。、,.（\(]")
        se = set()

        for result in re.finditer(regex, s):
            se.add(result.group(3))"""

    for result in re.finditer(accusation_regex, data["document"]["Title"]):
        arr = result.group(2).split("、")
        for x in arr:
            se.add(x)

    print(se)
    print(data["document"]["Title"])

    return se


def parse(data):
    result = {}
    # print(data["document"]["PJJG"])

    result["criminals"] = parse_criminals(data)

    return result
    result["term_of_imprisonment"] = parse_term_of_imprisonment(data)
    result["name_of_accusation"] = parse_name_of_accusation(data)
    result["name_of_law"] = parse_name_of_law(data)
    result["punish_of_money"] = parse_money(data)

    return result


def generate_fact(data):
    if "AJJBQK" in data["document"]:
        s = format_string(data["document"]["AJJBQK"])
        regex_list = [
            (r"(经审理查明|公诉机关指控|检察院指控|起诉书指控)([，：,:]?)([\s\S]*)([，。,]?)(足以认定|就上述指控|上述事实)", 2),
            (r"(经审理查明|公诉机关指控|检察院指控|起诉书指控)([，：,:]?)([\s\S]*)$", 2),
            (r"^([\s\S]*)([，。,]?)(足以认定|就上述指控|上述事实)", 0)
        ]

        fact = None

        for reg, num in regex_list:
            regex = re.compile(reg)
            result = re.findall(regex, s)
            if len(result) > 0:
                fact = result[0][num]
                break
        if not (fact is None):
            return fact

    if "SSJL" in data["document"]:
        s = format_string(data["document"]["SSJL"])
        regex_list = [
            (r"(经审理查明|公诉机关指控|检察院指控|起诉书指控)([，：,:]?)([\s\S]*)([，。,]?)(足以认定|就上述指控|上述事实)", 2),
            (r"(经审理查明|公诉机关指控|检察院指控|起诉书指控)([，：,:]?)([\s\S]*)$", 2),
            (r"^([\s\S]*)([，。,]?)(足以认定|就上述指控|上述事实)", 0)
        ]

        fact = None

        for reg, num in regex_list:
            regex = re.compile(reg)
            result = re.findall(regex, s)
            if len(result) > 0:
                fact = result[0][num]
                break
        if not (fact is None):
            return fact

    if "content" in data["document"]:
        s = format_string(data["document"]["content"])
        regex_list = [
            (r"(经审理查明|公诉机关指控|检察院指控|起诉书指控)([，：,:]?)([\s\S]*)([，。,]?)(足以认定|就上述指控|上述事实)", 2),
            (r"(经审理查明|公诉机关指控|检察院指控|起诉书指控)([，：,:]?)([\s\S])*事实一致", 2),
            (r"指控([，：,:])([\s\S]*)。本院认为", 1),
            (r"(经审理查明|公诉机关指控|检察院指控|起诉书指控)([，：,:]?)([\s\S])*《", 2),
        ]

        fact = None

        for reg, num in regex_list:
            regex = re.compile(reg)
            result = re.findall(regex, s)
            if len(result) > 0:
                fact = result[0][num]
                break
        if not (fact is None):
            return fact
    return None

    print(data["document"]["Title"])
    if "AJJBQK" in data["document"]:
        print(data["document"]["AJJBQK"])
    else:
        print("no AJJBQK")
    if "SSJL" in data["document"]:
        print(data["document"]["SSJL"])
    else:
        print("no SSJL")
    if "content" in data["document"]:
        print(data["document"]["content"])
    else:
        print("no content")
    print("")


def draw_out(in_path, out_path):
    print(in_path)
    inf = open(in_path, "r")
    ouf = open(out_path, "w")

    cnt = 0
    cx = 0
    for line in inf:
        try:
            data = json.loads(line)
            fact = generate_fact(data)
            if fact is None:
                continue
            # print(fact)
            data["meta"] = parse(data)
            """if not ("youqi" in data["meta"]["term_of_imprisonment"]) or len(
                    data["meta"]["term_of_imprisonment"]["youqi"]) <= 1:
                continue
            print(data["document"]["Title"])
            print("content", data["document"]["content"])
            print("fact", fact)
            if "PJJG" in data["document"]:
                print("result", data["document"]["PJJG"])
            else:
                print("result no result")
            print("meta", data["meta"])
            print("")"""

            cnt += 1
            if cnt % 5000 == 0:
                gg
                print(in_path, cnt, cx)
                # break

        except Exception as e:
            gg  # print(e)
            # gg


def work(from_id, to_id):
    for a in range(int(from_id), int(to_id)):
        print(str(a) + " begin to work")
        draw_out(os.path.join(in_path, str(a)), os.path.join(out_path, str(a)))
        print(str(a) + " work done")


if __name__ == "__main__":
    import multiprocessing

    process_pool = []

    for a in range(0, num_process):
        process_pool.append(
            multiprocessing.Process(target=work, args=(a * num_file / num_process, (a + 1) * num_file / num_process)))

    for a in process_pool:
        a.start()

    for a in process_pool:
        a.join()
