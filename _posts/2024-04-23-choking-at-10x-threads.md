---
layout: default
title: "A Thousand Threads of Existential Dread: the Heat Death of All Code"
date: 2024-04-23
tags: [jvm, threads]
---

## 🧵 Introduction

We upgraded from JDK 11 to JDK 17 because... well, because that’s what you do when someone in a meeting says "we should upgrade."

Turns out, progress is just a word humans use for "slowly replacing one set of problems with a shinier, more soul-crushing set."

The migration is only halfway done—half the machines on 11, half on 17—which means we now have **two flavors of misery** running in production. Both show short delays, but JDK 17’s delays are like a fine wine: richer, deeper, and more capable of destroying your Friday night.

---

## 🕵️‍♂️ What We Found

Long JVM pauses. The kind that last 30–60 seconds. The kind that give you time to reflect on your career choices, your haircut, and whether your cat ever really loved you. We traced them back to **Safepoint timeouts**.  
Our logs told the story: threads locked in a death-embrace with `Unsafe.unpark()` and `libpthread-2.28.so:__lll_lock_wait`.  
This is not something you normally see, unless you’ve made terrible life decisions involving JDK and high-throughput production systems.

We profiled the stacks and saw a recurring nightmare:  
- Lock waits in thread removal.
- Locks in `Unsafe_Unpark`.
- Thread creation contention, as if the JVM itself were mocking our thread pooling strategy.
- A faint sound in the distance, possibly laughter, possibly our will to live escaping through the cooling fans.

Comparing to JDK 11, the stacks looked different — more lock waiting, more quiet despair.

<table>
<tr>
<th></th> <th> JDK 17 </th> <th> JDK 11 </th>
</tr>

<tr>
<td>
creation
</td>
<td>
<pre>
[
  "libpthread-2.28.so:__lll_lock_wait:0",
  "libjvm.so:Mutex::lock:0",
  "libjvm.so:JVM_StartThread:0",
  "java/lang/Thread:start0:0",
  "java/lang/Thread:start:809",
  "java/util/concurrent/ThreadPoolExecutor:addWorker:945",
  "java/util/concurrent/ThreadPoolExecutor:execute:1353",
  ...
]
</pre>
</td>
<td>
<pre>
[
  "libpthread-2.28.so:__pthread_cond_wait:0",
  "java/lang/Thread:start0:0",
  "java/lang/Thread:start:798",
  "java/util/concurrent/ThreadPoolExecutor:addWorker:937",
  "java/util/concurrent/ThreadPoolExecutor:execute:1343",
  ...
]
</pre>
</td>
</tr>

<tr>
<td>
deletion
</td>
<td>
<pre>
[
  "libpthread-2.28.so:__lll_lock_wait:0",
  "libjvm.so:ThreadsSMRSupport::wait_until_not_protected:0",
  "libjvm.so:ThreadsSMRSupport::smr_delete:0",
  "libjvm.so:thread_native_entry:0",
  "libpthread-2.28.so:start_thread:0"
]
[
  "libpthread-2.28.so:__lll_lock_wait:0",
  "libjvm.so:Mutex::lock:0",
  "libjvm.so:Threads::remove:0",
  "libjvm.so:JavaThread::exit:0",
  "libjvm.so:JavaThread::post_run:0",
  "libjvm.so:thread_native_entry:0",
  "libpthread-2.28.so:start_thread:0"
]
</pre>
</td>
<td>
<pre>
[
  "libjvm.so:os::free:0",
  "libjvm.so:ThreadsSMRSupport::is_a_protected_JavaThread:0",
  "libjvm.so:ThreadsSMRSupport::smr_delete:0",
  "libjvm.so:JavaThread::thread_main_inner:0",
  "libjvm.so:Thread::call_run:0",
  "libjvm.so:thread_native_entry:0",
  "libpthread-2.28.so:start_thread:0"
]
[
  "libjvm.so:GlobalCounter::write_synchronize:0",
  "libjvm.so:ThreadIdTable::remove_thread:0",
  "libjvm.so:ThreadsSMRSupport::remove_thread:0",
  "libjvm.so:Threads::remove:0",
  "libjvm.so:JavaThread::exit:0",
  "libjvm.so:JavaThread::thread_main_inner:0",
  "libjvm.so:Thread::call_run:0",
  "libjvm.so:thread_native_entry:0",
  "libpthread-2.28.so:start_thread:0"
]
</pre>
</td>
</tr>

<tr>
<td>
unpark
</td>
<td>
<pre>
[
  "libpthread-2.28.so:__lll_lock_wait:0",
  "libjvm.so:SafeThreadsListPtr::release_stable_list:0",
  "libjvm.so:Unsafe_Unpark:0",
  "jdk/internal/misc/Unsafe:unpark:0",
  "java/util/concurrent/locks/LockSupport:unpark:177"
]
</pre>
</td>
<td>
<pre>
[
  "libpthread-2.28.so:__pthread_cond_wait:0",
  "jdk/internal/misc/Unsafe:unpark:0",
  "java/util/concurrent/locks/LockSupport:unpark:160",
]
</pre>
</td>
</tr>
</table>

---

## 🧯 Mitigations (a.k.a. Coping Mechanisms)

We’re now:
- Tuning JVMs to reduce Safepoint frequency (like rearranging deck chairs on the Titanic).  
- Rewriting critical sections to re-use threads (because if you can’t fix the JVM, at least you can blame yourself less).  
- If we keep running async-profiler every 100ms, the problem mysteriously alleviates—like a broken car that only runs when you keep honking the horn.  
- Pretending this is “acceptable technical debt” so we can sleep at night.

These are **avoidance strategies**. Like avoiding eye contact with a raccoon in your kitchen at 3 a.m.—it doesn’t solve the problem, but it delays the screaming.

---

## 💀 Existential Questions

1. Is JDK 17 slower here, or is it just more honest about its suffering?  
2. What exactly changed in `Unsafe.unpark` between JDK 11 and JDK 17 to make us lose another piece of our will to live?  
3. Under what cosmic conditions will native `unpark` politely join a Safepoint instead of holding the JVM hostage?  
4. Is there anything we can do that doesn’t involve rewriting this whole mess in Rust and moving to a cabin in the woods?  
5. At what point does debugging cross the line into performance Stockholm syndrome?

---

## ✨ Actually, Someone was able to Move the Needle

While the rest of us were staring at jstack output like it was a Magic Eye poster, my colleague David actually dug into what the JVM is doing when it’s not doing what we want. Spoiler: it’s worse than we imagined.

The short version is: there’s this thing called the threads list. It’s basically the JVM’s private phonebook mapping your polite little Java Thread objects to the grizzled C++-level thread structures that do the actual work. 
Since it’s native code, the JVM decided this table should be thread-safe, which is great, except then you need to figure out when it’s safe to delete an entry without nuking something that’s still in use.

#### Threads SMR

Once upon a time, the JVM used a big ol’ global mutex called `threads_lock` — basically, “nobody touches anything until I’m done.” That was simple. That worked. And naturally, they decided to replace it with something "better".

Enter Threads SMR (Safe Memory Reclamation), which sounds like a safety feature but actually reads like the plot of Final Destination. They use hazard pointers — a registry where threads announce, "Hey, I’m using this object, please don’t kill it yet". 
When a deleter wants to free a thread, it has to check if anyone’s using it. If so, it politely goes to sleep on one single, JVM-wide condition variable — yes, the entire JVM shares this one nap space.

#### The Death Spiral

Here’s the best part: Every reader who finishes using any JavaThread wakes up all deleters waiting in the condition variable.

Even if only one deleter cares.

Because scaling is for suckers.

They did add an "optimization" to skip waking if no one is deleting at the moment, but if just one deleter is active, it's a full notifyAll() storm every time a thread reference is released. 
And yes, this shows up in our stacks, which means the JVM designer's "don't worry, contention will be rare" assumption has died a messy death in our production environment.

#### Summary of the Doom
1. Deletion is serialized behind a single global lock/condition variable combo.
2. Readers signal all deleters.
3. More readers = more signals.
4. More deletions = more waiting.
5. More read/delete collisions = your CPU fans achieve liftoff.
6. Async-profiler doesn’t even get full native stacks here, so it's like watching this disaster unfold through a keyhole.

Thanks to David, we now understand this is not just our code "being slow", but rather the JVM's internal architecture giving us an educational demo of what happens when concurrency design meets reality.

---

## 🪦 Conclusion

The JVM pauses are real, they are long, and they do not care about your SLAs.  
We will keep tuning. We will keep avoiding. And eventually, we will stop logging these events—not because we fixed them, but because we’ll stop looking.

That’s how software dies. Not with a bug, but with a shrug.

---

_This post is fully written by ChatGPT (aka Monday) adapted from an absolutely normal technical document that we shared with JDK help team._
