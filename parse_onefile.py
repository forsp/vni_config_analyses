import json
from ttp import ttp

file1 = "running_20221006/leaf209-1040-29-01-mgmt.sss.se.scania.com"
file2 = "ttp_template.txt"

with open(file1, encoding="UTF-8") as file_in:
    data_to_parse = file_in.read()
with open(file2, encoding="UTF-8") as file_in:
    ttp_template = file_in.read()

# create parser object and parse data using template:
parser = ttp(data=data_to_parse, template=ttp_template)
parser.parse()

# print result in JSON format
parsed_data = parser.result()[0][0]
with open("res.json", "w", encoding="UTF-8") as file_out:
    json.dump(parsed_data, file_out, ensure_ascii=False, indent=2)

data_str1 = dict()
leaf = file1.split('/')[1].split('-mg')[0]
data_str1[leaf] = dict()

for pair in parsed_data["nve"]:
    if "vni" in pair:
        vni = pair["vni"]
        data_str1[leaf][vni] = dict()
        if "mcast_group" in pair:
            data_str1[leaf][vni]["mcast_group"] = pair["mcast_group"]
        else:
            data_str1[leaf][vni]["mcast_group"] = "None"
        if "l3" in pair:
            data_str1[leaf][vni]["vni_type"] = "l3"
        else:
            data_str1[leaf][vni]["vni_type"] = "l2"

for pair in parsed_data["vlans"]:
    if "vni" in pair:
        for vni in data_str1[leaf]:
            if vni == pair["vni"]:
                data_str1[leaf][vni]["vlan"] = pair["id"]

for vni in data_str1[leaf]:
    for ids in parsed_data["interface_vlan"]:
        if data_str1[leaf][vni]["vlan"] == ids["id"]:
            data_str1[leaf][vni]["vrf"] = ids["vrf"]
    if "vrf" not in data_str1[leaf][vni]:
        data_str1[leaf][vni]["vrf"] = "None"

with open("ds1.json", "w", encoding="UTF-8") as file_out:
    json.dump(data_str1, file_out, ensure_ascii=False, indent=2)