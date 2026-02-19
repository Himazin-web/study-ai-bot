import discord
from discord.ext import commands
import os
import datetime
import matplotlib.pyplot as plt
from PIL import Image
import io
import google.generativeai as genai
from dotenv import load_dotenv  # 追加

# .env ファイルやサーバーの環境変数を読み込む
load_dotenv()

# --- 設定 ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Geminiの設定（環境変数から取得）
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

study_log = []

@bot.event
async def on_ready():
    print(f"✅ ログイン成功: {bot.user}")

# 📚 勉強記録
@bot.command()
async def 記録(ctx, subject, hours: float):
    study_log.append((datetime.date.today(), subject, hours))
    await ctx.send(f"📝 {subject} を {hours}時間 記録したぞ！その調子だ。")

# 📊 勉強時間グラフ
@bot.command()
async def グラフ(ctx):
    if not study_log:
        await ctx.send("⚠️ まだデータがないぞ。まずは !記録 で勉強時間を教えてくれ。")
        return

    subjects = {}
    for _, sub, h in study_log:
        subjects[sub] = subjects.get(sub, 0) + h

    plt.figure()
    plt.bar(subjects.keys(), subjects.values())
    plt.title("Study Record")
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    await ctx.send(file=discord.File(buf, "graph.png"))

# 🧠 忘却曲線復習
@bot.command()
async def 復習(ctx):
    await ctx.send("⏳ **復習タイミングの鉄則**\n1日後 → 3日後 → 7日後 → 14日後\nこのタイミングで解き直せば、記憶は定着する。")

# 🗺 学習計画生成
@bot.command()
async def plan(ctx):
    await ctx.send("""
📅 **今日の学習軍略**
・英語 2h (単語+長文)
・数学 2h (苦手分野の例題)
・理科 1h (重要項目の暗記)
・復習 1h (昨日のミスを潰す)
""")

# 📷 画像問題読み取り
@bot.command()
async def 読み取り(ctx):
    if not ctx.message.attachments:
        await ctx.send("📸 解析したい画像を添付してこのコマンドを打ってくれ。")
        return

    async with ctx.typing():
        try:
            attachment = ctx.message.attachments[0]
            image_bytes = await attachment.read()
            image = Image.open(io.BytesIO(image_bytes))

            prompt = "この画像に書かれている文字をすべて書き起こし、さらに受験生の助けになるように重要ポイントを短く解説してください。"
            response = model.generate_content([prompt, image])
            
            await ctx.send(f"📖 **軍師の解析結果:**\n\n{response.text[:1900]}")
        except Exception as e:
            await ctx.send(f"❌ 解析中に事故が発生した：{e}")

# 🎯 戦略
@bot.command()
async def 戦略(ctx):
    await ctx.send("""
🔥 **必勝受験戦略**
・**英語**: 毎朝の単語は儀式だ。欠かすな。
・**数学**: 青チャートの例題を完璧にしろ。
・**理科**: 基礎問題精講を3周回せ。
""")

# 環境変数からトークンを読み込む
token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("Error: DISCORD_TOKEN が設定されていません。")