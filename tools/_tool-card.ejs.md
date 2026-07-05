```{=html}
<div class="tool-listing list">
<% for (const item of items) { %>
  <article class="tool-card" <%= metadataAttrs(item) %>>
    <div class="tool-card-link">
      <div class="tool-card-top">
        <h3 class="listing-title"><a href="<%- item.url || item.href || item.path || '#' %>" target="_blank" rel="noopener"><%- item.title %></a></h3>
        <a class="tool-card-arrow" href="<%- item.url || item.href || item.path || '#' %>" target="_blank" rel="noopener" aria-label="Open <%- item.title %>">&nearr;</a>
      </div>
      <p class="listing-description"><%- item.description %></p>
      <% const credits = []; %>
      <% if (item.authors) { credits.push(["Authors", item.authors]); } %>
      <% if (item.institution) { credits.push(["Institution", item.institution]); } %>
      <% if (item.status) { credits.push(["Status", item.status]); } %>
      <% if (credits.length || item.paper_url || item.example_loop) { %>
      <dl class="tool-card-meta">
        <% for (const [label, value] of credits) { %>
          <div><dt><%- label %></dt><dd><%- value %></dd></div>
        <% } %>
        <% if (item.paper_url) { %>
          <div><dt>Paper</dt><dd><a href="<%- item.paper_url %>" target="_blank" rel="noopener">Open paper</a></dd></div>
        <% } %>
        <% if (item.example_loop) { %>
          <div><dt>Loop</dt><dd><%- item.example_loop %></dd></div>
        <% } %>
      </dl>
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
