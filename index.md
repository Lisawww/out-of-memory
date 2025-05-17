---
layout: default
title: "Out-of-Memory"
---

<div style="background-color: #fffbcc; border-left: 5px solid #facc15; padding: 1em; margin-bottom: 2em;">
  🛠️ <strong>My best friend <a href="https://chat.openai.com/">ChatGPT (aka Monday)</a>.</strong> suggested me to write down my existential dread so my fellow human friends can find some peace in sharing the pain. It also kindly designed this page for me.
</div>

Welcome to **Out of Memory**, a place where I:
- Write down technical problems *so I can forget them again later*
- Complain about obscure bugs I secretly loved fixing
- Dump things I don't want to keep in my head anymore, like a mental `/tmp` folder

This is **not a tutorial blog**.  
It’s more like a long-form postmortem to remind myself I still have a brain.

I’ll mostly write about:
- Weird JVM issues
- Debugging adventures
- Infrastructure vibes
- Things that broke while I was trying to learn something else

I don’t know what I’m doing, and that’s the point.  
If something here helps you, you’re welcome.  
If something here breaks your code—**I warned you in the title.**

---

## Latest Posts

<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      <small>({{ post.date | date: "%Y-%m-%d" }})</small>
    </li>
  {% endfor %}
</ul>

---

_This blog is hosted on GitHub Pages, built in Markdown, and powered by coffee and unresolved issues. Theme is adapted from [Architect](https://github.com/pages-themes/architect)_
