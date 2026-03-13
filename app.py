from flask import Flask, jsonify, Response, send_from_directory
import requests, os
from datetime import datetime

app = Flask(__name__)

WORDS = [
    {"word":"fascinating","meaning":"Extremely interesting","joe_says":"The most fascinating thing about it is how nobody talks about it.","use_it":"That's a fascinating perspective — I hadn't thought of it that way."},
    {"word":"legitimate","meaning":"Real, valid, genuinely serious","joe_says":"That's a legitimate concern and I think most people just ignore it.","use_it":"Do you think that's a legitimate reason or just an excuse?"},
    {"word":"nuanced","meaning":"Having subtle differences; not black and white","joe_says":"It's a very nuanced situation and people want a simple answer.","use_it":"The reality is way more nuanced than the media makes it seem."},
    {"word":"compelling","meaning":"Powerfully convincing or impossible to ignore","joe_says":"He made a really compelling argument that I couldn't disagree with.","use_it":"That's a compelling case — I need to look into that more."},
    {"word":"simultaneously","meaning":"At the same time","joe_says":"You can simultaneously believe two things that seem contradictory.","use_it":"I was simultaneously impressed and terrified by what he said."},
    {"word":"articulate","meaning":"Able to express ideas clearly and fluently","joe_says":"She's one of the most articulate people I've ever talked to.","use_it":"He's incredibly articulate — every word is exactly right."},
    {"word":"genuinely","meaning":"Truly and sincerely, not fake","joe_says":"I genuinely believe most people are doing the best they can.","use_it":"I genuinely don't know how they pulled that off."},
    {"word":"fundamentally","meaning":"At the most basic and important level","joe_says":"Fundamentally, the problem is that nobody wants to do the hard work.","use_it":"We fundamentally disagree on how to approach this."},
    {"word":"resilient","meaning":"Able to recover quickly from difficulty","joe_says":"Humans are incredibly resilient — we adapt to almost anything.","use_it":"She's one of the most resilient people I know."},
    {"word":"momentum","meaning":"The force that keeps something moving or growing","joe_says":"Once you build momentum it becomes almost impossible to stop.","use_it":"Don't break the momentum — keep going while it's working."},
    {"word":"inevitable","meaning":"Certain to happen, impossible to avoid","joe_says":"At some point the shift was inevitable — it was just a matter of when.","use_it":"Conflict was inevitable given how different they are."},
    {"word":"profound","meaning":"Very deep and meaningful","joe_says":"That's a profound statement and most people just brush past it.","use_it":"The impact of that decision was more profound than anyone expected."},
    {"word":"deliberate","meaning":"Done on purpose; intentional and careful","joe_says":"Everything about that decision was deliberate — nothing was accidental.","use_it":"You have to be deliberate about how you spend your time."},
    {"word":"narrative","meaning":"The story or version of events people believe","joe_says":"The mainstream narrative doesn't match what the data actually shows.","use_it":"They're trying to control the narrative before the truth comes out."},
    {"word":"groundbreaking","meaning":"Innovative and completely new","joe_says":"That research was groundbreaking — nobody had even thought of it before.","use_it":"It's not groundbreaking but it's a solid improvement."},
    {"word":"acknowledge","meaning":"To admit or recognize that something is true","joe_says":"You have to acknowledge that both sides have valid points.","use_it":"I want to acknowledge that I was wrong about that."},
    {"word":"insane","meaning":"Unbelievably extreme (informal native use)","joe_says":"It's insane how much misinformation is just accepted as fact.","use_it":"The amount of work they put into that is absolutely insane."},
    {"word":"wild","meaning":"Surprising, crazy, or hard to believe","joe_says":"It's kind of wild when you think about how recent all of this is.","use_it":"That's wild — I had no idea that was even possible."},
    {"word":"brutal","meaning":"Very harsh, direct, or extreme","joe_says":"That's brutal honesty right there and I respect it.","use_it":"The feedback was brutal but exactly what I needed to hear."},
    {"word":"perspective","meaning":"A particular way of thinking about something","joe_says":"It really shifts your perspective when you hear it from their side.","use_it":"From my perspective, the whole thing doesn't add up."},
]

PATTERNS = [
    {"pattern":"Here's the thing about [topic]...","example":"Here's the thing about success — most people want it but don't want what it takes.","tip":"Use this to signal you're about to say something real and direct."},
    {"pattern":"What's interesting is [observation]","example":"What's interesting is nobody actually talks about the cost of not trying.","tip":"Sounds thoughtful and analytical — very natural in conversation."},
    {"pattern":"The reality is [truth]","example":"The reality is most people give up right before it starts working.","tip":"Sounds confident and grounded — great for professional settings."},
    {"pattern":"I genuinely believe [opinion]","example":"I genuinely believe that consistency beats talent almost every time.","tip":"'Genuinely' makes it sound sincere, not just filler."},
    {"pattern":"It's kind of wild when you think about [fact]","example":"It's kind of wild when you think about how fast everything is changing.","tip":"Very natural, casual, native — sounds like a real person talking."},
    {"pattern":"At some point you have to [action]","example":"At some point you have to stop planning and just start doing.","tip":"Sounds wise and direct without being aggressive."},
    {"pattern":"I'd argue [point]","example":"I'd argue this is the better approach and here's why.","tip":"Sounds educated and confident — great in debates and meetings."},
    {"pattern":"That's one of those things where [situation]","example":"That's one of those things where you don't realize how important it is until it's gone.","tip":"Makes people nod — very relatable and conversational."},
    {"pattern":"The most [adjective] part is [observation]","example":"The most underrated part is how much your environment shapes your habits.","tip":"Native speakers love this structure — direct and punchy."},
    {"pattern":"You can't [action] without [other action]","example":"You can't expect different results without changing something fundamental.","tip":"Sounds logical and clear — great for making arguments."},
]

GRAMMAR = [
    {"tip":"Drop 'very' — use a stronger word","wrong":"That was very good.","right":"That was exceptional / outstanding / remarkable.","why":"Native speakers replace 'very' with precise powerful adjectives."},
    {"tip":"Use contractions naturally","wrong":"I am not sure that is the right answer.","right":"I'm not sure that's the right answer.","why":"Without contractions you sound like a textbook."},
    {"tip":"Say 'That makes sense' not 'I understand'","wrong":"I understand what you mean.","right":"That makes sense. / That tracks.","why":"Native speakers confirm understanding with 'That makes sense'."},
    {"tip":"Use 'I'd say' to give opinions smoothly","wrong":"In my opinion the deadline is too short.","right":"I'd say the deadline is a bit unrealistic honestly.","why":"'I'd say' is casual and native — 'in my opinion' sounds translated."},
    {"tip":"Use 'Honestly' to add emphasis","wrong":"I really think we need to change the plan.","right":"Honestly, we need to rethink the whole plan.","why":"'Honestly' signals you're about to say something real — very native."},
    {"tip":"Use 'end up' for unplanned results","wrong":"Finally I became the team leader.","right":"I ended up becoming the team leader.","why":"'End up' is extremely common in native speech for unexpected outcomes."},
    {"tip":"Use 'I'd argue' to sound confident but not arrogant","wrong":"I think maybe possibly it could be better.","right":"I'd argue this is the better approach.","why":"Sounds educated and direct — used a lot in podcasts and debates."},
    {"tip":"Use 'Though' at the end instead of 'But' at the start","wrong":"But I disagree with that approach.","right":"I disagree with that approach, though.","why":"'Though' at the END sounds more natural and native in casual speech."},
]


CEO_PLANS = [
    {
        "learn": "Read 10 pages of Zero to One by Peter Thiel — focus on what makes a startup monopoly.",
        "followup": "Follow up with one person you met this week. Send a short message: what you learned from them.",
        "routine": "No phone for the first 30 minutes after waking. Journal 3 things you want to accomplish today."
    },
    {
        "learn": "Watch a 20-minute interview with a founder on YouTube — write down 1 thing they did differently.",
        "followup": "Check your last 5 sent emails. Is there anyone waiting on you? Reply today.",
        "routine": "Cold water on your face, 10 deep breaths, then read your top 3 goals out loud before touching your phone."
    },
    {
        "learn": "Study one successful startup's early pitch deck — Airbnb, Uber, or Dropbox. What problem did they solve?",
        "followup": "Message one mentor or person you admire. Ask one specific question, not just 'how are you'.",
        "routine": "Write your MIT — Most Important Task — before breakfast. Do that first, everything else second."
    },
    {
        "learn": "Learn what Product-Market Fit means. Look up how Slack, Notion, or Figma found theirs.",
        "followup": "Review your LinkedIn connections. Find one person in your target industry to connect with today.",
        "routine": "Spend 5 minutes standing outside in fresh air before sitting at your desk. CEOs call this a reset."
    },
    {
        "learn": "Read a startup post-mortem — why did a company fail? Google 'startup failure post mortem'. Learn from it.",
        "followup": "Send a thank you note to someone who helped you recently. Be specific about what they did.",
        "routine": "Plan tomorrow the night before. Write 3 tasks before you sleep — wake up with a clear head."
    },
    {
        "learn": "Study how successful CEOs price their product. Read about value-based pricing vs cost-based pricing.",
        "followup": "Pick one idea you have and tell one real person about it today. Get their honest reaction.",
        "routine": "Exercise for at least 20 minutes. Elon, Bezos, Jobs — all prioritized physical movement."
    },
    {
        "learn": "Study the concept of customer discovery. How do you validate an idea before building it?",
        "followup": "Review your week so far — what did you say you would do but haven't? Do one of those things today.",
        "routine": "Eat a real breakfast with no screens. Your brain runs your business — fuel it properly."
    },
    {
        "learn": "Research one local Toronto startup that got funded this year. What problem are they solving?",
        "followup": "Send one cold email to someone you want to learn from. Keep it under 5 sentences.",
        "routine": "Write down your long-term vision — where do you want to be in 3 years? Read it every morning."
    },
    {
        "learn": "Learn the difference between B2B and B2C business models. Which fits your idea better and why?",
        "followup": "Go back to a conversation you left incomplete. Finish it — follow-through is your reputation.",
        "routine": "Set your phone to Do Not Disturb until 9 AM. Own your morning before the world takes it."
    },
    {
        "learn": "Study how to write a one-pager for your business idea. Practice with any idea — real or hypothetical.",
        "followup": "Check in on a classmate or friend working on something. Support builds your network.",
        "routine": "Drink water before coffee. Spend 10 minutes reading something that has nothing to do with school."
    },
    {
        "learn": "Learn about go-to-market strategy. How do startups get their first 100 customers?",
        "followup": "Is there a project or commitment you've been avoiding? Send a quick update to whoever is waiting.",
        "routine": "Make your bed. It is the first win of the day — it builds the discipline habit that CEOs live by."
    },
    {
        "learn": "Study the lean startup method — Build, Measure, Learn. How does it apply to your own ideas?",
        "followup": "Text someone you haven't spoken to in 2 weeks. Relationships are your most valuable asset.",
        "routine": "Do a 5-minute brain dump — write everything on your mind. Clears the noise so you can focus."
    },
    {
        "learn": "Research how startups raise a seed round. What do investors look for in a first meeting?",
        "followup": "Review your goals from last week. Did you hit them? Be honest with yourself — no excuses.",
        "routine": "Avoid checking social media until after your first task is complete. Protect your morning energy."
    },
    {
        "learn": "Study one CEO's daily schedule — Jeff Bezos, Sara Blakely, or Jensen Huang. What patterns do you see?",
        "followup": "Reconnect with a professor or advisor. Ask for one piece of advice on your current direction.",
        "routine": "Spend 5 minutes before bed reviewing what went well today. Confidence is built from small wins."
    },
]


def get_weather():
    try:
        r = requests.get("https://wttr.in/Toronto?format=j1", timeout=5)
        w = r.json()["current_condition"][0]
        return {"temp": int(w["temp_C"]), "desc": w["weatherDesc"][0]["value"], "error": None}
    except Exception as e:
        return {"temp": 10, "desc": "Partly Cloudy", "error": str(e)}


@app.route("/")
def index():
    html = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Minje's Shortcuts</title>
<style>
  body { background:#000; color:#fff; font-family:-apple-system,sans-serif; text-align:center; padding:40px 20px; }
  h1 { font-size:26px; margin-bottom:8px; }
  p { color:#aaa; margin-bottom:40px; }
  a.btn { display:block; background:#ff3b30; color:#fff; text-decoration:none;
          padding:18px; border-radius:14px; font-size:18px; font-weight:600;
          margin:16px auto; max-width:320px; }
  a.btn.blue { background:#007aff; }
  small { color:#555; font-size:13px; display:block; margin-top:32px; }
</style>
</head>
<body>
<h1>Minje's Daily Shortcuts</h1>
<p>Open this page on iPhone Safari and tap to install</p>
<a class="btn" href="/shortcuts/morning.shortcut">⬇️ Install Morning Briefing</a>
<a class="btn blue" href="/shortcuts/carplay.shortcut">⬇️ Install CarPlay English</a>
<small>daily-briefing-z4gw.onrender.com</small>
</body>
</html>"""
    return Response(html, mimetype="text/html")


@app.route("/shortcuts/<filename>")
def serve_shortcut(filename):
    return send_from_directory("static", filename,
                               mimetype="application/x-apple-aspen-config",
                               as_attachment=True)


@app.route("/api/daily")
def api_daily():
    day     = datetime.now().timetuple().tm_yday
    word    = WORDS[day % len(WORDS)]
    pattern = PATTERNS[day % len(PATTERNS)]
    grammar = GRAMMAR[day % len(GRAMMAR)]
    weather = get_weather()

    morning_spoken = (
        f"Good morning Minje. Today is {datetime.now().strftime('%A, %B %d')}. "
        f"Toronto weather: {weather['temp']} degrees, {weather['desc']}. "
        f"Word of the day: {word['word']}. Meaning: {word['meaning']}. "
        f"Joe Rogan uses it like this: {word['joe_says']}"
    )
    carplay_spoken = (
        f"Hey Minje! English tip for your drive. "
        f"Today's pattern: {pattern['pattern']}. "
        f"Example: {pattern['example']}. "
        f"Grammar tip: {grammar['tip']}. "
        f"Correct version: {grammar['right']}. "
        f"Have a great drive!"
    )

    return jsonify({
        "date":            datetime.now().strftime("%A, %B %d"),
        "weather":         weather,
        "word":            word,
        "pattern":         pattern,
        "grammar":         grammar,
        "morning_spoken":  morning_spoken,
        "carplay_spoken":  carplay_spoken,
    })


@app.route("/api/morning")
def api_morning():
    """Returns plain text for iPhone Shortcuts — just Speak Text, no JSON parsing needed"""
    day     = datetime.now().timetuple().tm_yday
    word    = WORDS[day % len(WORDS)]
    weather = get_weather()
    plan    = CEO_PLANS[day % len(CEO_PLANS)]
    text = (
        f"Good morning Minje. Today is {datetime.now().strftime('%A, %B %d')}. "
        f"Toronto weather: {weather['temp']} degrees, {weather['desc']}. "
        f"Here are your 3 plans for today. "
        f"Plan 1, Learn: {plan['learn']} "
        f"Plan 2, Follow up: {plan['followup']} "
        f"Plan 3, Morning routine: {plan['routine']} "
        f"Word of the day: {word['word']}. {word['meaning']}. "
        f"Joe Rogan uses it like this: {word['joe_says']}. "
        f"Now go make today count."
    )
    return Response(text, mimetype="text/plain")


@app.route("/today")
def today_page():
    """Beautiful HTML daily note — shortcut just opens this URL"""
    day     = datetime.now().timetuple().tm_yday
    word    = WORDS[day % len(WORDS)]
    pattern = PATTERNS[day % len(PATTERNS)]
    grammar = GRAMMAR[day % len(GRAMMAR)]
    weather = get_weather()
    plan    = CEO_PLANS[day % len(CEO_PLANS)]
    date    = datetime.now().strftime("%A, %B %d")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>Minje · {date}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0a0a0a; color: #f0f0f0; font-family: -apple-system, sans-serif;
         padding: 20px 16px 60px; max-width: 480px; margin: 0 auto; }}
  .date {{ font-size: 13px; color: #888; margin-bottom: 4px; letter-spacing: 1px; text-transform: uppercase; }}
  .weather {{ font-size: 15px; color: #aaa; margin-bottom: 24px; }}
  .section {{ background: #141414; border-radius: 16px; padding: 18px; margin-bottom: 14px; }}
  .section-title {{ font-size: 11px; color: #888; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 14px; }}
  .plan {{ display: flex; gap: 12px; margin-bottom: 14px; }}
  .plan:last-child {{ margin-bottom: 0; }}
  .plan-icon {{ font-size: 20px; flex-shrink: 0; margin-top: 1px; }}
  .plan-label {{ font-size: 11px; color: #ff6b6b; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; }}
  .plan-text {{ font-size: 15px; color: #e8e8e8; line-height: 1.5; }}
  .word {{ font-size: 26px; font-weight: 700; color: #fff; margin-bottom: 4px; letter-spacing: 1px; }}
  .meaning {{ font-size: 14px; color: #aaa; margin-bottom: 14px; }}
  .quote {{ font-size: 14px; color: #e8e8e8; line-height: 1.6; border-left: 3px solid #ff6b6b; padding-left: 12px; margin-bottom: 10px; font-style: italic; }}
  .use-it {{ font-size: 13px; color: #888; line-height: 1.5; }}
  .pattern-text {{ font-size: 16px; font-weight: 600; color: #fff; margin-bottom: 8px; }}
  .example {{ font-size: 14px; color: #aaa; line-height: 1.6; margin-bottom: 8px; font-style: italic; }}
  .tip {{ font-size: 13px; color: #ff6b6b; }}
  .grammar-tip {{ font-size: 14px; font-weight: 600; color: #fff; margin-bottom: 10px; }}
  .wrong {{ font-size: 13px; color: #888; margin-bottom: 6px; }}
  .right {{ font-size: 14px; color: #4cd964; font-weight: 500; }}
  .footer {{ text-align: center; font-size: 14px; color: #555; margin-top: 24px; }}
</style>
</head>
<body>
  <div class="date">{date}</div>
  <div class="weather">🌤 Toronto · {weather['temp']}°C · {weather['desc']}</div>

  <div class="section">
    <div class="section-title">🎯 Today's 3 Plans</div>
    <div class="plan">
      <div class="plan-icon">📚</div>
      <div><div class="plan-label">Learn</div><div class="plan-text">{plan['learn']}</div></div>
    </div>
    <div class="plan">
      <div class="plan-icon">📩</div>
      <div><div class="plan-label">Follow Up</div><div class="plan-text">{plan['followup']}</div></div>
    </div>
    <div class="plan">
      <div class="plan-icon">☀️</div>
      <div><div class="plan-label">Routine</div><div class="plan-text">{plan['routine']}</div></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">📖 Word of the Day</div>
    <div class="word">{word['word'].upper()}</div>
    <div class="meaning">{word['meaning']}</div>
    <div class="quote">"{word['joe_says']}"</div>
    <div class="use-it">Try it → "{word['use_it']}"</div>
  </div>

  <div class="section">
    <div class="section-title">🗣 English Pattern</div>
    <div class="pattern-text">"{pattern['pattern']}"</div>
    <div class="example">"{pattern['example']}"</div>
    <div class="tip">💡 {pattern['tip']}</div>
  </div>

  <div class="section">
    <div class="section-title">✏️ Grammar Tip</div>
    <div class="grammar-tip">{grammar['tip']}</div>
    <div class="wrong">❌ {grammar['wrong']}</div>
    <div class="right">✅ {grammar['right']}</div>
  </div>

  <div class="footer">💪 Make today count.</div>
</body>
</html>"""
    return Response(html, mimetype="text/html")


@app.route("/api/note")
def api_note():
    """Returns clean summarized note for Notes app"""
    day     = datetime.now().timetuple().tm_yday
    word    = WORDS[day % len(WORDS)]
    pattern = PATTERNS[day % len(PATTERNS)]
    grammar = GRAMMAR[day % len(GRAMMAR)]
    weather = get_weather()
    plan    = CEO_PLANS[day % len(CEO_PLANS)]
    date    = datetime.now().strftime("%A, %B %d")

    text = f"""🌅 {date}
🌤 Toronto {weather['temp']}°C · {weather['desc']}

─────────────────
🎯 TODAY'S 3 PLANS

✅ Learn
{plan['learn']}

✅ Follow Up
{plan['followup']}

✅ Routine
{plan['routine']}

─────────────────
📖 Word: {word['word'].upper()}
{word['meaning']}
💬 "{word['use_it']}"

─────────────────
🗣 Pattern: {pattern['pattern']}
→ "{pattern['example']}"

✏️ Grammar: {grammar['tip']}
✅ "{grammar['right']}"

─────────────────
💪 Make today count."""
    return Response(text, mimetype="text/plain")


@app.route("/api/carplay")
def api_carplay():
    """Returns plain text for CarPlay Shortcuts"""
    day     = datetime.now().timetuple().tm_yday
    pattern = PATTERNS[day % len(PATTERNS)]
    grammar = GRAMMAR[day % len(GRAMMAR)]
    text = (
        f"Hey Minje! English tip for your drive. "
        f"Today's pattern: {pattern['pattern']}. "
        f"Example: {pattern['example']}. "
        f"Tip: {pattern['tip']}. "
        f"Grammar: {grammar['tip']}. "
        f"Correct version: {grammar['right']}. "
        f"Have a great drive!"
    )
    return Response(text, mimetype="text/plain")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5051))
    app.run(host="0.0.0.0", port=port, debug=False)
