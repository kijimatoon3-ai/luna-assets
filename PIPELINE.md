# ルナ 毎週パイプライン(スケジュール実行用の手順書)

TikTok @ai_loto_luna(Metricool ブランド 7390724「ai_loto_luna」、ルナ専用。旧ブランド 6989756 は開花亭BIS専用で、触らない)。抽せんは月曜・木曜の18:45。
実行は毎週 火曜・金曜 07:07(JST)。必ず先に CONCEPT.md を読む(v3: 2026-10-14 改訂)。

## 2本構成(1回の実行で動画を2本)
- A) 結果発表(オフ・カーディガン・ギャル口調、45〜60秒): 今日 19:30 に予約(企画書の火・金19〜21時を4週間テスト)。
- B) 予想(オン・白ジャケット、75〜90秒): 次の抽せん日(金曜実行なら月曜、火曜実行なら木曜)の 12:00 に予約(企画書の11:30〜13:00を4週間テスト)。
- 重複チェックは A(今日19:30)と B(次の抽せん日12:00)を別々に見る。無い方だけ作る。
- 結果動画(A)は「直前に予想動画を公開した回」だけ作る。予想を出していない回は作らない(第2145回は対象外)。

## 守ること(破らない)
- 当せん確率が上がる、とは絶対に言わない。「当てる方法ではない」「確率はどの6数字でも同じ」を毎回入れる。
- 自虐(頭が悪そう等)・当選金額・取り分・山分けの話はしない。「被りにくさ」を柱にしない(冒頭の小ネタ程度)。
- 結果を確認できない/2か所で食い違う/動画が失敗したときは、投稿せずに止めて、ユーザーに通知。間違った結果の動画を出すより止める。
- 同じ回の投稿が予約・公開済みなら何もしない(二重投稿禁止)。迷ったら止める。
- 動画の長さは 60〜90秒(予想は最大90秒)。超えたら台本を詰めて作り直す(1回だけ)。
- 数字は data/picks・data/history.json・data/week_summary.json のものだけ使う(手書き禁止)。

## 手順
0. リポジトリ kijimatoon3-ai/luna-assets が無ければ add_repo(access=push)→ git clone。作業はリポジトリのルート。
1. 直前に終わった回 D を決める(data/loto6_all.xlsx の最終行の次、または最新の抽せん日(月・木))。次の回 N = D+1。N の抽せん日: D が月曜の回なら木曜、D が木曜の回なら月曜。
2. 重複チェック(上記)。両方ある → 終了。
3. 結果の取得: WebFetch で次を順に試す。本数字6個とボーナスは**2か所以上で一致**を確認。
   - https://tokaikensyo.com/campaignwinning/loto6/
   - https://www.mk-mode.com/rails/loto/loto6
   - https://loto-life.net/csv/download(最新回数の確認用)
   - https://takarakuji-loto.jp/tousenp.html
   - みずほ銀行のページは JS 描画で空になるので使わない。口数(1〜5等)と賞金は表がある1か所から取る。取れない場合は止める。
4. data/result.json を作る: {"draw":D,"date":"YYYY-MM-DD","nums":[6個昇順],"bonus":b,"counts":[1〜5等口数],"prizes":[1〜5等賞金],"carry":キャリーオーバー}
5. python3 scripts/weekly.py --result data/result.json --next N --next-date "M/D 曜"
   → cards/answer_<D>.png(答え合わせ)、cards/hook_<N>.png(冒頭フック: 1等が出た回の割合)、cards/numbers_<N>.png(ルナの6数字)、cards/pred_<N>.png(旧・比較カード。使わない)、data/picks/<N>.json、data/scoreboard.json、data/week_summary.json。
5b. 整合性チェック(必須): python3 scripts/validate.py --draw D --next N。NG なら動画を作らず止めて通知。
6. git add -A; git commit; git push(カードを raw.githubusercontent.com で公開するため)。
   カードURL: https://raw.githubusercontent.com/kijimatoon3-ai/luna-assets/main/cards/<ファイル名>
7. 動画を HeyGen create_video_from_studio で作る(aspectRatio "9:16"、全シーン voice_id 9U1EOQDnE3aBBuViHEYj、voice_settings.speed 1.1)。
   【予想動画 B(白ジャケット avatar f25ca49937d1451b870b6dcc4408775b)】基準は第2146回の動画(HeyGen 3937f22da7953a98801a10a9e64bc7f6、87秒)。構成:
   1) avatar: 冒頭2秒で意外な事実(例「ロト6、約7割の回で、日本のだれかが1等を当ててるって知ってた?」)。毎回同じ言い回しにしない。
   2) image hook_<N>.png: 全<N-1>回中の1等が出た回数・割合(カードの数字をそのまま読む)、自分が当てる確率は 610万分の1・どの6数字でも同じ。
   3) avatar: 「当てる方法じゃなく、データを分析して予想して、結果を毎回公開して検証する」→「第N回の6数字はこちら」。
   4) image numbers_<N>.png: 「1つ目、○。2つ目、○…」と1個ずつ、最後にまとめて読む。「全<N-1>回のデータを分析して選びました」。
   5) avatar: 「当たる保証はありません。遊びとして見てね。あなたの6数字もコメントで教えて。答え合わせは<金曜|火曜>の朝に出すよ。フォローして待っててね」。
   【結果動画 A(カーディガン avatar a194463ace6340de863dc0ece760ff61)】45〜60秒:
   1) avatar: 冒頭2秒で結果(「一致、0個…!」「ルナ、2個一致!」など、毎回変える)。続けて「やっほー、ルナだよ。第D回の答え合わせ」。
   2) image answer_<D>.png: 当せん番号、ルナの一致数、今回のメモ(1等の口数)、「無作為な6数字の一致は平均で約0.84個」、ルナの通算。ランダムは参考として一言だけ。
   3) avatar: 学びを1つ(例:「外れても確率は同じ。1等は○口出たよ」)、次の予想の日時を予告、コメント誘導(「あなたの一致数も教えて」)。
   get_video で completed まで待つ(目安3〜4分、30秒ごと)。失敗したら1回だけ作り直し、それでも失敗なら止めて通知。
8. Metricool createScheduledPost(blogId 7390724、providers tiktok、tiktokData {isAigc:true, privacyOption:PUBLIC_TO_EVERYONE, title}、media は video_url)。
   - B(予想): 次の抽せん日 12:00。キャプション冒頭は冒頭の事実と610万分の1、続けて【第N回 AI予想】ルナの6数字、注意書き(当たる保証なし・確率はどの6数字も同じ・抽せんは毎回独立・エンタメ)、ハッシュタグ(#ロト6 #ロト6予想 #AI予想 #AIロト研究員ルナ #宝くじ)。firstCommentText「あなたの6数字もコメントで教えてね!答え合わせは○曜の朝に出すよ」。
   - A(結果): 今日 19:30。【第D回 答え合わせ】一致数と1等の口数、注意書き、同じハッシュタグ。firstCommentText「あなたの一致数も教えて!次の予想は○曜のお昼に出すよ」。
9. Projects ツールの claude/luna-method-v1.md の「戦績」を data/scoreboard.json の通算に更新する。
10. 最後に、何を作って何時に予約したか、ルナの通算一致数を一行でまとめて報告。

## 補足
- 2026-10-13にルナ専用ブランドに分離し、有料プランに変更済み。週4本(結果発表2+予想2)で運用する。開花亭BISの投稿(旧ブランド 6989756)は一切触らない。
- ルナの外見: 予想=白ジャケット(オン)、答え合わせ=カーディガン(オフ・ギャル)。固定。
- 効果測定: 3〜4本たまったら Metricool で時間帯別の再生数・最後まで見られた割合を比べ、投稿時間を調整する(ユーザーと相談)。
