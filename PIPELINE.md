# ルナ 毎週パイプライン(スケジュール実行用の手順書)

TikTok @ai_loto_luna(Metricool ブランド 6989756)。抽せんは月曜・木曜の18:45。
実行は毎週 火曜・金曜 07:07(JST)。
【2本構成(2026-10-09 ユーザー確認)】1回の実行で動画を2本作る。
 A) 結果発表だけ(オフ・カーディガン・ギャル口調、約45秒): シーン1(冒頭は結果から)→答え合わせカード→締め「次の予想は<月曜|木曜>の抽せん前に出すよ」。今日10:00に予約。
 B) 予想だけ(オン・白ジャケット、約50秒): 冒頭「ルナの<リベンジ等>数字を公開します。第N回、<月曜|木曜>の予想です」→予想カード→CTA(前回の結果に一言触れる)。次の抽せん日(金曜実行なら月曜、火曜実行なら木曜)の18:00に予約。
 以降の手順7・8の「1本」は、A・B それぞれに読み替える(Bの台本は手順7のシーン3〜5を使う)。
 重複チェックは A(今日10:00)と B(次の抽せん日18:00)の両方を見る。どちらも無ければ作る。片方だけ有れば無い方だけ作る。

## 守ること(破らない)
- 当せん確率が上がる、とは絶対に言わない。「当たったときの取り分」と「ルナ vs ランダムの公開検証」だけ。
- 結果を確認できない/2か所で食い違う/動画が失敗したときは、投稿せずに止めて、ユーザーに通知(PushNotification があれば使い、最終メッセージにも書く)。間違った結果の動画を出すより止める。
- すでに同じ回の投稿が予約・公開されている場合は、何もしない(二重投稿禁止)。
- 公開前にユーザーが確認できない前提。迷ったら止める。

## 手順
0. リポジトリ kijimatoon3-ai/luna-assets が無ければ add_repo(access=push)→ git clone。作業はリポジトリのルート。
1. 直前に終わった回 D を決める。data/loto6_all.xlsx の最終行の次、または最新の抽せん日(月・木)。次の回 N = D+1。
   N の抽せん日: D が月曜の回なら木曜、D が木曜の回なら月曜。
2. 重複チェック: data/picks/<N>.json が既にあり、かつ Metricool(getScheduledPosts, brandId 6989756, Asia/Tokyo)に今日10:00以降の TikTok 予約がある → 終了(何もしない)。
3. 結果の取得: WebFetch で次を順に試す(抽せん翌朝は更新済みのはず)。本数字6個とボーナスは**2か所以上で一致**を確認。
   - https://tokaikensyo.com/campaignwinning/loto6/
   - https://www.mk-mode.com/rails/loto/loto6
   - https://loto-life.net/csv/download(最新回数の確認用)
   - https://takarakuji-loto.jp/tousenp.html
   - みずほ銀行のページは JS 描画で空になるので使わない。
   口数(1〜5等)と賞金は表がある1か所から取る。取れない場合は止める。
4. data/result.json を作る:
   {"draw":D,"date":"YYYY-MM-DD","nums":[6個昇順],"bonus":b,"counts":[1〜5等口数],"prizes":[1〜5等賞金],"carry":キャリーオーバー}
5. python3 scripts/weekly.py --result data/result.json --next N --next-date "M/D 曜"
   → cards/answer_<D>.png、cards/pred_<N>.png、data/picks/<N>.json、data/scoreboard.json、data/week_summary.json ができる。
5b. 整合性チェック(必須): python3 scripts/validate.py --draw D --next N。NG なら動画を作らず止めて通知。
   通れば、data/history.json に「予想(数字・根拠)→結果→一致数→通算」が回ごとに1本でつながっている。
   予想も結果も必ずここ(data/picks/<回>.json と data/week_summary.json)の数字だけを使う。台本に数字を手で書き写さない(コピーして使う)。
6. git add -A; git commit; git push(カードを raw.githubusercontent.com で公開するため)。
   カードURL: https://raw.githubusercontent.com/kijimatoon3-ai/luna-assets/main/cards/<ファイル名>
7. 動画を HeyGen create_video_from_studio で作る(aspectRatio "9:16"、全シーン voice_id 9U1EOQDnE3aBBuViHEYj、voice_settings.speed 1.1)。
   台本は data/week_summary.json の数値で作る。ギャル部分は砕けた口調、予想部分はフォーマル。「昨日の第D回」と言う(実行は抽せんの翌朝)。
   - シーン1 avatar_video(オフ): avatar_id a194463ace6340de863dc0ece760ff61、「やっほー、ルナだよ。昨日の第D回の結果、見た?」+ルナの結果への一言(外れ/当たり/ランダムに勝った/負けた)。
   - シーン2 image: cards/answer_<D>.png に、ナレーション(当せん番号、ルナ一致○個、ランダム一致○個、勝敗、通算)。
   - 予想動画(B)は、ルナの6数字を「1つ目、20。2つ目、25。…」と1個ずつ紹介してから、最後に6数字をまとめて読む。ランダムは続けてまとめて読むだけでよい。
   - 結果動画(A)には、予想の根拠と実際の結果の照合を一言入れる(例: 「人気薄を選んだけど、当たりは人気の数字に寄ってた」)。当たった場合も外れた場合も、「当選確率は上がらない」前提を崩さない。
   - シーン3 avatar_video(オン): avatar_id f25ca49937d1451b870b6dcc4408775b、「ここからは、第N回の予想です。ルナは、人気のない数字を選びます。」
   - シーン4 image: cards/pred_<N>.png に、ナレーション(ルナの6数字、ランダムの6数字、「どっちが勝つか勝負です」)。
   - シーン5 avatar_video(オン): 「当たる保証はありません。遊びとして見てください。ルナとランダム、どっちが勝つと思いますか。コメントで教えてください。」
   【冒頭2秒のルール(2026-10-08 決定)】動画の最初の2秒(約10文字以内)で、結果か結論を言って止める。あいさつや前置きは後ろに回す。
   - シーン1の1文目を、結果から入る短い一言にする。例: 「ルナ、ランダムに勝った!」「ルナ、また外した…」「引き分け!」「一致、まさかの○個!」。
   - その直後に「やっほー、ルナだよ」と続ける(名前の出だしは固定)。
   - 表紙(カバー)は、シーン1の笑顔のカットを使う。
   - 冒頭の一言は毎回同じ言い回しにしない。直近の2本と重ならないようにする。
   全体 60〜80秒に収める。ナレーションは短く、数字は区切って読む(例「に、にじゅういち、…」ではなく「2、21、30、34、35、43」と書く)。
   get_video で completed まで待つ(目安4分、30秒ごと)。失敗したら1回だけ作り直し、それでも失敗なら止めて通知。
8. Metricool createScheduledPost(blogId 6989756): 今日 10:00 JST、providers tiktok、
   tiktokData {isAigc:true, privacyOption:PUBLIC_TO_EVERYONE, title:"第N回ロト6 ルナの予想と答え合わせ"}、media は video_url。
   キャプション: 【第D回 答え合わせ+第N回 AI予想】の見出し、ルナ/ランダムの一致数、「当たる保証なし・抽せんは毎回独立・エンタメ」、ハッシュタグ(#ロト6 #ロト6予想 #AI予想 #AIロト研究員ルナ #宝くじ)。
   firstCommentText: 「ルナとランダム、どっちが多く当たると思う?コメントで教えて!」
9. Projects ツールの claude/luna-method-v1.md の「戦績」を data/scoreboard.json の通算に更新する。
10. 最後に、何を作って何時に予約したか、ルナ vs ランダムの通算を一行でまとめて報告。

## 補足
- 月の公開枠(Metricool、他ブランドと共有)は残りが少ない。週2本まで。増やさない(ユーザー決定)。
- ルナの外見: 予想=白ジャケット(オン)、答え合わせ=カーディガン(オフ・ギャル)。固定。
- 効果測定: 3〜4本たまったら Metricool で時間帯別の再生数・最後まで見られた割合を比べ、投稿時間を調整する(ユーザーと相談)。
