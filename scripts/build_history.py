"""data/history.json を作る: 回ごとに「予想(数字・根拠)→結果→一致数→通算→手法の指標」を1本につなぐ共通データ。"""
import json, glob, os
sb = {x["draw"]: x for x in json.load(open("data/scoreboard.json"))["rows"]}
hist = []; cl = cr = 0
for f in sorted(glob.glob("data/picks/*.json"), key=lambda p: int(os.path.basename(p)[:-5])):
    p = json.load(open(f)); d = p["next"]; r = sb.get(d)
    e = {"draw": d, "analysis_through": p["draws"], "oos_corr": round(p["oos_corr"], 4),
         "luna": p["luna"], "random": p["random"], "percentile_luna": round(p["percentile_luna"], 3),
         "basis_unpopular": p["unpopular"], "basis_popular": p["popular"], "result": None}
    if r:
        cl += r["luna_hit"]; cr += r["random_hit"]
        e["result"] = {"nums": r["nums"], "bonus": r["bonus"], "luna_hit": r["luna_hit"], "random_hit": r["random_hit"],
                       "cum_luna": cl, "cum_random": cr}
    hist.append(e)
json.dump(hist, open("data/history.json", "w"), ensure_ascii=False, indent=1); print("history", len(hist))
