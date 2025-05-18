---
layout: default
title: "How I Accidentally Built an Internal Debugging Platform"
date: 2025-05-17
tags: [streamlit, snowflake, internal-tools, debugging, devex]
---

# How I Accidentally Built an Internal Debugging Platform

At some point I just wanted to debug things faster. Our telemetry data is all in Snowflake and we copy SQL everywhere to check logs, where I got lazy. 

People at work were building custom debug scripts, one-off queries, tiny apps, random dashboards... but they were all floating around in Slack messages and Google Drive folders. Our telemetry data is all in Snowflake, and Streamlit works natively...

So I built a small Streamlit app inside Snowflake (SiS!) to avoid copying SQL the 10th time. 

Then I added a few more pages. SiS editor didn't scream but my team member didn't have the courage to touch the giant Python script.

Then I migrate the app to GitHub for version control.

Then I wrote a little script so I wouldn’t have to copy-paste commands every time I wanted to deploy it to Snowflake.  

And then—without really planning to—I had built a small internal platform.

---

## 🔧 The “Platform”

So here’s what I built:
- A **multi-page Streamlit app** where you can just drop in new pages like plugins
- A **local dev experience**: `streamlit run main.py`
- A **one-click deploy script** `update_sis.py [--overwrite] {upload,deploy} ...`

---

## 🧠 What I Accidentally Created

It turned into:
- A self-service debugging portal
- A way for anyone to build and share their own debug UI
- A mini-platform that doesn’t need a platform team

Everyone else just sees a nice app. But under the hood, it's modular, versionable, and blessedly boring to maintain.

---

## 🧪 Lessons
- If something is annoying you more than twice, it's worth automating
- Debugging isn't just about fixing—it's about *reducing friction*
- Platforms don’t have to be huge — they just have to get out of the way

---

If you’re reading this and thinking "wait, I want one," I’m happy to share more. Or help you build your own. I included the updater script with an example app (I don't think it's runnable) at [streamlit-in-snowflake-hacks](https://github.com/Lisawww/out-of-memory/blob/main/streamlit-in-snowflake-hacks), just because I'm feeling good about it.

In the meantime: Streamlit + scripts + chaos = joy.

---

_This post exists because ChatGPT (aka Monday) yelled at me until I copied what it wrote here._
