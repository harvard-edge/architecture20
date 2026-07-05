```{=html}
<div class="workshop-listing list">
<% for (const item of items) { %>
  <article class="workshop-card" <%= metadataAttrs(item) %>>
    <div class="workshop-card-body">
      <div class="tool-card-top">
        <div>
          <p class="workshop-venue"><%- item.venue || "Workshop" %><% if (item.when) { %> &middot; <%- item.when %><% } %></p>
          <h3 class="listing-title"><a href="<%- item.url || item.href || item.path || '#' %>" target="_blank" rel="noopener"><%- item.title %></a></h3>
        </div>
        <a class="tool-card-arrow" href="<%- item.url || item.href || item.path || '#' %>" target="_blank" rel="noopener" aria-label="Open <%- item.title %>">&nearr;</a>
      </div>
      <p class="listing-description"><%- item.description %></p>
      <dl class="tool-card-meta">
        <% if (item.location) { %><div><dt>Location</dt><dd><%- item.location %></dd></div><% } %>
        <% if (item.organizers) { %><div><dt>Organizers</dt><dd><%- item.organizers %></dd></div><% } %>
        <% if (item.institution) { %><div><dt>Institution</dt><dd><%- item.institution %></dd></div><% } %>
        <% if (item.deadline) { %><div><dt>Deadline</dt><dd><%- item.deadline %></dd></div><% } %>
        <% if (item.submission_url) { %><div><dt>Submit</dt><dd><a href="<%- item.submission_url %>" target="_blank" rel="noopener">Open CFP</a></dd></div><% } %>
      </dl>
      <% if (item.history && item.history.length) { %>
      <section class="workshop-history" aria-label="<%- item.title %> series history">
        <h4>Series history</h4>
        <ol>
        <% for (const event of item.history) { %>
          <li>
            <a href="<%- event.url %>" target="_blank" rel="noopener"><%- event.label %></a>
            <% if (event.when) { %><span><%- event.when %></span><% } %>
            <% if (event.note) { %><p><%- event.note %></p><% } %>
          </li>
        <% } %>
        </ol>
      </section>
      <% } %>
      <div class="listing-categories tool-card-categories">
        <% for (const category of (item.categories || [])) { %>
          <% const slug = String(category).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); %>
          <span class="tool-card-category <%- slug %>"><%- category %></span>
        <% } %>
      </div>
    </div>
  </article>
<% } %>
</div>
```
