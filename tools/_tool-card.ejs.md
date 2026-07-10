```{=html}
<div class="tool-listing list">
<% for (const item of items) { %>
  <% const primaryUrl = item.url || item.href || item.path || "#"; %>
  <% const categories = Array.isArray(item.categories) ? item.categories : []; %>
  <% const primaryCategory = categories[0] || ""; %>
  <% const primarySlug = String(primaryCategory).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); %>
  <% const tags = Array.isArray(item.tags) ? item.tags : []; %>
  <% const availabilityLabels = { runnable: "Runnable", source_available: "Source available", benchmark_available: "Benchmark available", dataset_available: "Dataset available", paper_only: "Paper only", unverified: "Unverified" }; %>
  <% const availability = item.artifact_availability || "unverified"; %>
  <article class="tool-card <%= primarySlug ? `tool-card-${primarySlug}` : "" %>" <%= metadataAttrs(item) %>>
    <div class="tool-card-link">
      <a class="tool-card-hitarea" href="<%= primaryUrl %>" target="_blank" rel="noopener" aria-label="Open <%= item.title %>"></a>
      <div class="tool-card-top">
        <h3 class="listing-title"><%= item.title %></h3>
        <span class="tool-card-arrow" aria-hidden="true">&nearr;</span>
      </div>
      <div class="tool-card-status" aria-label="Artifact availability and link verification">
        <span class="availability-badge availability-<%= availability %>"><%= availabilityLabels[availability] || availabilityLabels.unverified %></span>
        <span class="verification-date"><% if (item.last_verified) { %>Link checked <%= item.last_verified %><% } else { %>Link not verified<% } %></span>
      </div>
      <p class="listing-description"><%= item.description %></p>
      <% if (item.authors || item.institution || item.submitted_by) { %>
      <div class="tool-card-credit">
        <% if (item.authors) { %>
          <span><%= item.authors %></span>
        <% } %>
        <% if (item.institution) { %>
          <span><%= item.institution %></span>
        <% } %>
        <% if (item.submitted_by) { %>
          <span>submitted by <%= item.submitted_by %></span>
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
