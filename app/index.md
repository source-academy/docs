---
layout: home
hero:
  name: Source Academy Documentation
  tagline: The languages of Source Academy, and documentation for the people who build it.
---

## Source Academy languages

<div class="landing-grid">
<a class="landing-card" href="/javascript/" target="_self">
<strong>JavaScript</strong>
<span>The Source sublanguages of JavaScript (§1 to §4) used in SICP JS: specifications and documentation of the libraries.</span>
</a>
<a class="landing-card" href="/python/" target="_self">
<strong>Python</strong>
<span>The Python sublanguages (§1 to §4): specifications and documentation.</span>
</a>
</div>

## For developers

<div class="landing-grid">
<a class="landing-card" href="/developer/architecture/">
<strong>Architecture</strong>
<span>How the frontend, backend, grader, Conductor, the directories, the evaluators and the plugins fit together.</span>
</a>
<a class="landing-card" href="/developer/writing-a-visualizer-plugin">
<strong>Writing a visualizer plugin</strong>
<span>How to make a tool that shows a program's execution in the workspace.</span>
</a>
<a class="landing-card" href="/developer/contributing">
<strong>Contributing</strong>
<span>How to propose and make a change in any repository.</span>
</a>
<a class="landing-card" href="/developer/">
<strong>All developer pages</strong>
<span>Node.js version, comments, and the rest.</span>
</a>
</div>

<style>
.landing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin: 16px 0 32px;
}
.landing-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px 20px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  text-decoration: none;
  transition: border-color 0.2s;
}
.landing-card:hover {
  border-color: var(--vp-c-brand-1);
}
.landing-card span {
  color: var(--vp-c-text-2);
  font-size: 14px;
  line-height: 1.5;
}
</style>
