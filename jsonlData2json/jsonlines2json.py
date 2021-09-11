import jsonlines
import json
jsonLinesPath = "data4label_214.jsonl"
jsonPath = r"result0902/news_json00.json"
i = 1
new_json = []
with open(jsonLinesPath, "r+", encoding="utf8") as f:
    for item in jsonlines.Reader(f):
        new_json.append({
            "itemId": i,
            "info": item
        })
        i += 1


# with open("result0901/news_json{nums}.json".format(nums=i), "w") as w:
with open(jsonPath, "w") as w:
    json.dump(new_json, w, ensure_ascii=False)
    print("已生成json文件...")
