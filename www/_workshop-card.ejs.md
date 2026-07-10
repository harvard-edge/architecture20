```{=html}
<div class="workshop-listing list">
<% const activeItems = items.filter((item) => item.status === "active"); %>
<% const archivedItems = items.filter((item) => item.status === "archived"); %>
<section class="workshop-registry-section" aria-labelledby="active-workshops-title">
  <div class="section-heading compact-heading">
    <h2 id="active-workshops-title">Active workshops</h2>
  </div>
  <% if (activeItems.length === 0) { %>
  <div class="registry-empty-state" role="status">
    <strong>No active calls are listed.</strong>
    <span>Prior events remain below as an archive. Submit a current workshop for maintainer review.</span>
  </div>
  <% } %>
  <div class="workshop-card-grid">
<% for (const item of activeItems) { %>
  <article class="workshop-card" <%= metadataAttrs(item) %>>
    <div class="workshop-card-body">
      <div class="tool-card-top">
        <div>
          <p class="workshop-venue"><span class="registry-status registry-status-active">Active</span> <%- item.venue || "Workshop" %><% if (item.when) { %> &middot; <%- item.when %><% } %></p>
          <h3 class="listing-title"><a href="<%- item.url %>" target="_blank" rel="noopener"><%- item.title %></a></h3>
        </div>
        <a class="tool-card-arrow" href="<%- item.url %>" target="_blank" rel="noopener" aria-label="Open <%- item.title %>">&nearr;</a>
      </div>
      <p class="listing-description"><%- item.description %></p>
      <dl class="tool-card-meta">
        <% if (item.location) { %><div><dt>Location</dt><dd><%- item.location %></dd></div><% } %>
        <% if (item.organizers) { %><div><dt>Organizers</dt><dd><%- item.organizers %></dd></div><% } %>
        <% if (item.institution) { %><div><dt>Institution</dt><dd><%- item.institution %></dd></div><% } %>
        <% if (item.deadline) { %><div><dt>Deadline</dt><dd><%- item.deadline %></dd></div><% } %>
        <% if (item.submission_url) { %><div><dt>Submit</dt><dd><a href="<%- item.submission_url %>" target="_blank" rel="noopener">Open CFP</a></dd></div><% } %>
        <% if (item.last_verified) { %><div><dt>Verified</dt><dd><%- item.last_verified %></dd></div><% } %>
      </dl>
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
</section>

<% if (archivedItems.length) { %>
<section class="workshop-registry-section" aria-labelledby="archived-workshops-title">
  <div class="section-heading compact-heading">
    <h2 id="archived-workshops-title">Workshop archive</h2>
    <p>Past events are retained for their programs, materials, and series history. Submission links are removed after an event closes.</p>
  </div>
  <div class="workshop-card-grid">
<% for (const item of archivedItems) { %>
  <article class="workshop-card" <%= metadataAttrs(item) %>>
    <div class="workshop-card-body">
      <div class="tool-card-top">
        <div>
          <p class="workshop-venue"><span class="registry-status registry-status-archived">Archived</span> <%- item.venue || "Workshop" %><% if (item.when) { %> &middot; <%- item.when %><% } %></p>
          <h3 class="listing-title"><a href="<%- item.url %>" target="_blank" rel="noopener"><%- item.title %></a></h3>
        </div>
        <a class="tool-card-arrow" href="<%- item.url %>" target="_blank" rel="noopener" aria-label="Open archived <%- item.title %>">&nearr;</a>
      </div>
      <p class="listing-description"><%- item.description %></p>
      <dl class="tool-card-meta">
        <% if (item.location) { %><div><dt>Location</dt><dd><%- item.location %></dd></div><% } %>
        <% if (item.organizers) { %><div><dt>Organizers</dt><dd><%- item.organizers %></dd></div><% } %>
        <% if (item.last_verified) { %><div><dt>Verified</dt><dd><%- item.last_verified %></dd></div><% } %>
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
</section>
<% } %>
</div>
```
