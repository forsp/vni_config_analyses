import json
from ttp import ttp
import sys, os

folder = sys.argv[1]
#folder = "running_20221006"
filetmp = "ttp_template.txt"

data_str = dict()
# obtaining first data structure from parsed data
with open(filetmp, encoding="UTF-8") as file_in:
    ttp_template = file_in.read()

for filename in os.scandir(folder):
    if "leaf" not in filename.path:
        continue
    leaf = filename.path.split('/')[1].split('-mg')[0]
    with open(filename.path, encoding="UTF-8") as file_in:
        data_to_parse = file_in.read()
    parser = ttp(data=data_to_parse, template=ttp_template)
    parser.parse()
    parsed_data = parser.result()[0][0]
    with open("res.json", "w", encoding="UTF-8") as file_out:
        json.dump(parsed_data, file_out, ensure_ascii=False, indent=2)
    data_str[leaf] = dict()
    if "nve" not in parsed_data:
        print(f"File without nve: {filename.path}")
        continue
    for pair in parsed_data["nve"]:
        if "vni" in pair:
            vni = pair["vni"]
            data_str[leaf][vni] = dict()
            if "mcast_group" in pair:
                data_str[leaf][vni]["mcast_group"] = pair["mcast_group"]
            else:
                data_str[leaf][vni]["mcast_group"] = "None"
            if "l3" in pair:
                data_str[leaf][vni]["vni_type"] = "l3"
            else:
                data_str[leaf][vni]["vni_type"] = "l2"
    for pair in parsed_data["vlans"]:
        if "vni" in pair:
            for vni in data_str[leaf]:
                if vni == pair["vni"]:
                    data_str[leaf][vni]["vlan"] = pair["id"]
    for vni in data_str[leaf]:
        for ids in parsed_data["interface_vlan"]:
            if data_str[leaf][vni]["vlan"] == ids["id"]:
                data_str[leaf][vni]["vrf"] = ids["vrf"]
        if "vrf" not in data_str[leaf][vni]:
            data_str[leaf][vni]["vrf"] = "None"

# writing first data structure to file (optional)
# with open("ds1.json", "w", encoding="UTF-8") as file_out:
#     json.dump(data_str, file_out, ensure_ascii=False, indent=2)

# obtaining second data structure
data_str2 = dict()
temp_config = dict() #dict of all "config-device" pairs with dupplicates

for leaf in data_str:
    for vni in data_str[leaf]:
        if vni not in data_str2:
            data_str2[vni] = []
            temp_config[vni] = []

for vni2 in data_str2:
    for leaf in data_str:
        for vni in data_str[leaf]:
            if vni2 == vni:
                config = dict()
                config["config"] = data_str[leaf][vni]
                config["devices"] = leaf
                temp_config[vni].append(config)
# searching for devices with the same config
for vni in temp_config:
    for item in temp_config[vni]:
        istag = False
        for i in range(len(data_str2[vni])):
            if item["config"] == data_str2[vni][i]["config"]:
                data_str2[vni][i]["devices"].append(item["devices"])
                istag = True
        if istag == False:
            tempconf = dict()
            tempconf["config"] = item["config"]
            tempconf["devices"] = [item["devices"]]
            data_str2[vni].append(tempconf)

for vni in data_str2:
    if len(data_str2[vni]) > 1:
        print(f"Vni with more than one configuration: {vni}")
# with open("temp.json", "w", encoding="UTF-8") as file_out:
#     json.dump(temp_config, file_out, ensure_ascii=False, indent=2)
with open("ds2.json", "w", encoding="UTF-8") as file_out:
    json.dump(data_str2, file_out, ensure_ascii=False, indent=2)
