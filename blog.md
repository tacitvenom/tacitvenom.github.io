---
layout: page
title: Blog
---

<p class="message">
  Learning about the world we live in, one story at a time.
</p>

<div class="posts">
  {% for post in site.posts %}
  <div class="post">
    <h2 class="post-title">
      <a href="{{ post.url | absolute_url }}">
        {{ post.title }}
      </a>
    </h2>

    <span class="post-date">{{ post.date | date_to_string }}</span>

    {{ post.excerpt }}

    <a href="{{ post.url | absolute_url }}" class="read-more">Read more →</a>
  </div>
  {% endfor %}
</div>

{% if site.posts.size == 0 %}
<p>No blog posts yet. Check back soon for updates!</p>
{% endif %}

## Topics

My blog covers various aspects of the world that interests me and which I would like to view through the lens of data.

## Subscribe

Stay updated with my latest blog posts by subscribing to the [RSS feed](/atom.xml).

## Guest Posts

Interested in contributing a guest post? I occasionally feature articles from other professionals in the tech industry. [Contact me](/contact) with your proposal.
