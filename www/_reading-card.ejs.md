```{=html}
<div class="reading-listing list">
<% for (const item of items) { %>
  <article class="reading-card" <%= metadataAttrs(item) %>>
    <div class="reading-card-body">
      <div class="tool-card-top">
        <div>
          <p class="reading-kind"><%- item.kind || "Resource" %><% if (item.venue) { %> &middot; <%- item.venue %><% } %><% if (item.when) { %> &middot; <%- item.when %><% } %></p>
          <h3 class="listing-title"><a href="<%- item.url || item.href || item.path || '#' %>" target="_blank" rel="noopener"><%- item.title %></a></h3>
        </div>
        <a class="tool-card-arrow" href="<%- item.url || item.href || item.path || '#' %>" target="_blank" rel="noopener" aria-label="Open <%- item.title %>">&nearr;</a>
      </div>
      <p class="listing-description"><%- item.description %></p>
      <dl class="tool-card-meta">
        <% if (item.authors) { %><div><dt>Authors</dt><dd><%- item.authors %></dd></div><% } %>
        <% if (item.doi) { %><div><dt>DOI</dt><dd><%- item.doi %></dd></div><% } %>
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
```
