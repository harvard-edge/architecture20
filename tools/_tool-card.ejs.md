```{=html}
<div class="tool-listing list">
<% for (const item of items) { %>
  <% const primaryUrl = item.url || item.href || item.path || "#"; %>
  <% const categories = Array.isArray(item.categories) ? item.categories : []; %>
  <% const tags = Array.isArray(item.tags) ? item.tags : []; %>
  <% const links = [
    ["Paper", item.paper_url],
    ["Docs", item.docs_url],
    ["Artifact", item.artifact_url],
  ].filter((entry) => entry[1]); %>
  <% const loopRole = item.loop_role || item.example_loop; %>
  <% const creditParts = []; %>
  <% if (item.authors) { creditParts.push(item.authors); } %>
  <% if (item.institution) { creditParts.push(item.institution); } %>
  <% if (item.submitted_by) { creditParts.push(`submitted by ${item.submitted_by}`); } %>
  <article class="tool-card" <%= metadataAttrs(item) %>>
    <div class="tool-card-link">
      <a class="tool-card-hitarea" href="<%= primaryUrl %>" target="_blank" rel="noopener" aria-label="Open <%= item.title %>"></a>
      <div class="tool-card-top">
        <h3 class="listing-title"><%= item.title %></h3>
        <span class="tool-card-arrow" aria-hidden="true">&nearr;</span>
      </div>
      <p class="listing-description"><%= item.description %></p>
      <% if (loopRole) { %>
      <p class="tool-card-loop"><span>Loop role</span><%= loopRole %></p>
      <% } %>
      <% if (links.length) { %>
      <div class="tool-card-links" aria-label="Links for <%= item.title %>">
        <% for (const [label, href] of links) { %>
          <a href="<%= href %>" target="_blank" rel="noopener"><%= label %></a>
        <% } %>
      </div>
      <% } %>
      <% if (creditParts.length || item.status) { %>
      <div class="tool-card-credit">
        <% if (creditParts.length) { %>
          <span><%= creditParts.join(" · ") %></span>
        <% } %>
        <% if (item.status) { %>
          <span><%= item.status %></span>
        <% } %>
      </div>
      <% } %>
      <div class="listing-categories tool-card-categories">
        <% for (const category of categories) { %>
          <% const slug = String(category).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); %>
          <span class="tool-card-category <%= slug %>"><%= category %></span>
        <% } %>
        <% for (const tag of tags) { %>
          <span class="tool-card-tag"><%= tag %></span>
        <% } %>
      </div>
    </div>
  </article>
<% } %>
</div>
```
