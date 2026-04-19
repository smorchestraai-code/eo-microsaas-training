Code ships with 80.
 
Boris Cherny runs Claude Code at Anthropic. His team's entire playbook is around 2.5k tokens, roughly 100 lines. They ship 20-30 PRs a day with it.
 
Here's what's actually inside:
 
1️⃣ 𝗣𝗹𝗮𝗻 𝗠𝗼𝗱𝗲 𝗗𝗲𝗳𝗮𝘂𝗹𝘁 For any non-trivial task (3+ steps or architectural decisions), start in plan mode. If something goes sideways, stop and re-plan instead of pushing forward. Write detailed specs upfront to kill ambiguity.
 
2️⃣ 𝗦𝘂𝗯𝗮𝗴𝗲𝗻𝘁 𝗦𝘁𝗿𝗮𝘁𝗲𝗴𝘆 Use subagents liberally to keep the main context window clean. Offload research, exploration, and parallel analysis. One task per subagent. That's how Boris throws more compute at complex problems without bloating the main context.
 
3️⃣ 𝗦𝗲𝗹𝗳-𝗜𝗺𝗽𝗿𝗼𝘃𝗲𝗺𝗲𝗻𝘁 𝗟𝗼𝗼𝗽 After any correction from the user, update tasks/lessons.md with the pattern. Write rules that prevent the same mistake. This is the compounding part. Every mistake becomes a rule. Every rule reduces future mistakes.
 
4️⃣ 𝗩𝗲𝗿𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻 𝗕𝗲𝗳𝗼𝗿𝗲 𝗗𝗼𝗻𝗲 Never mark a task complete without proving it works. Ask yourself: "Would a staff engineer approve this?" Run tests, check logs, demonstrate correctness. Boris says giving Claude a way to verify its work 2-3x's the final output quality.
 
5️⃣ 𝗗𝗲𝗺𝗮𝗻𝗱 𝗘𝗹𝗲𝗴𝗮𝗻𝗰𝗲 For non-trivial changes, pause and ask "is there a more elegant way?" If a fix feels hacky, tell Claude: "Knowing everything I know now, implement the elegant solution." Skip this for obvious fixes, don't over-engineer.
 
6️⃣ 𝗔𝘂𝘁𝗼𝗻𝗼𝗺𝗼𝘂𝘀 𝗕𝘂𝗴 𝗙𝗶𝘅𝗶𝗻𝗴 When given a bug report, just fix it. Don't ask for hand-holding. Point at logs, errors, failing tests, then resolve them. Zero context switching from the user.
 
Traditional approach: 
↳ Write long, detailed prompts every session 
↳ Hope Claude remembers your style and standards 
↳ Fix the same mistakes over and over 
↳ Manual verification after every change
 
Boris's approach: 
↳ Let CLAUDEmd hold the memory 
↳ Add a new rule every time Claude gets something wrong 
↳ Verification loops baked into the process 
↳ Multiple Claude instances running in parallel
 
The difference isn't complexity. It's compounding.
 
Every correction becomes durable context. Every session starts smarter than the last. 80-90% of Claude Code itself is now written using Claude Code. That's the kind of leverage a well-maintained CLAUDEmd gives you.
 
Over to you: how long is your CLAUDEmd right now?