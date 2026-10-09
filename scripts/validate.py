"""動画生成前の整合性チェック。1つでも失敗したら exit 1(動画を作らない)。
使い方: python3 scripts/validate.py --draw D --next N [--script 台本.txt ...]
  D = 結果が確定した回(答え合わせ対象)、N = 次の回(予想対象)
"""
import argparse, json, os, sys, datetime, openpyxl
ap = argparse.ArgumentParser(); ap.add_argument("--draw", type=int, required=True); ap.add_argument("--next", type=int, required=True)
ap.add_argument("--script", nargs="*", default=[]); a = ap.parse_args()
D, N = a.draw, a.next; errs = []
def chk(c, m):
    if not c: errs.append(m)
chk(N == D + 1, f"次回は直前回の次であること(D={D}, N={N})")
ws = openpyxl.load_workbook("data/loto6_all.xlsx").active
rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0]]
last = rows[-1]; chk(last[0] == D, f"履歴の最終行が第{D}回であること(実際 {last[0]})")
chk([r[0] for r in rows] == list(range(rows[0][0], rows[0][0] + len(rows))), "履歴の回が連番で欠けなし")
nums = list(last[2:8]); bonus = last[8]
chk(len(set(nums)) == 6 and all(1 <= x <= 43 for x in nums), "当せん数字が6個・重複なし・1〜43")
chk(bonus not in nums and 1 <= bonus <= 43, "ボーナスが本数字と重複せず1〜43")
dt = last[1]; chk(dt.weekday() in (0, 3), f"抽せん日が月・木であること({dt:%Y-%m-%d} {dt.weekday()})")
pD = json.load(open(f"data/picks/{D}.json")) if os.path.exists(f"data/picks/{D}.json") else None
chk(pD is not None, f"第{D}回の保存済み予想(data/picks/{D}.json)がある")
pN = json.load(open(f"data/picks/{N}.json")) if os.path.exists(f"data/picks/{N}.json") else None
chk(pN is not None, f"第{N}回の予想(data/picks/{N}.json)がある")
if pN: chk(pN["draws"] == D, f"第{N}回の予想が第{D}回までのデータで計算されている(draws={pN['draws']})")
if pD: chk(pD["next"] == D and pD["draws"] == D - 1, f"第{D}回の予想が第{D-1}回までのデータで作られている")
sb = json.load(open("data/scoreboard.json"))["rows"]; r = next((x for x in sb if x["draw"] == D), None)
chk(r is not None, "戦績に第%d回がある" % D)
if r and pD:
    chk(r["luna"] == pD["luna"] and r["random"] == pD["random"], "戦績の予想数字が、予想時に保存した数字と同じ")
    chk(r["nums"] == nums and r["bonus"] == bonus, "戦績の当せん数字が履歴と同じ")
for f in (f"cards/answer_{D}.png", f"cards/pred_{N}.png"): chk(os.path.exists(f), f"{f} がある")
for s in a.script:
    t = open(s).read()
    for label, ns in (("答え合わせ", nums), ("ルナ予想", pN["luna"] if pN else []), ("ランダム予想", pN["random"] if pN else [])):
        pass
    chk(f"第{N}回" in t or f"{N}" in t, f"{s}: 第{N}回が台本にある")
    for old in (D - 1, D - 2):
        chk(f"第{old}回" not in t, f"{s}: 古い回(第{old}回)が台本に混ざっていない")
print("OK" if not errs else "NG"); [print(" -", e) for e in errs]; sys.exit(1 if errs else 0)
