"use client";

import { useMemo, useState } from "react";

import type { FacetConfig } from "@/lib/sections";

type Item = Record<string, any>;

interface EntityListProps {
  title: string;
  subtitle: string;
  items: Item[];
  facets?: FacetConfig[];
}

function valueToText(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (Array.isArray(value)) return value.join(", ");
  return String(value);
}

function snippet(value: unknown, limit = 180): string {
  const text = valueToText(value).replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
  if (!text) return "";
  if (text.length <= limit) return text;
  return `${text.slice(0, limit - 1)}…`;
}

export default function EntityList({ title, subtitle, items, facets = [] }: EntityListProps) {
  const [query, setQuery] = useState("");
  const [facetValues, setFacetValues] = useState<Record<string, string>>({});

  const optionsByFacet = useMemo(() => {
    const map: Record<string, string[]> = {};
    for (const facet of facets) {
      const values = new Set<string>();
      for (const item of items) {
        const value = valueToText(item[facet.key]);
        if (value) values.add(value);
      }
      map[facet.key] = [...values].sort((a, b) => a.localeCompare(b));
    }
    return map;
  }, [facets, items]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return items.filter((item) => {
      if (q) {
        const hay = JSON.stringify(item).toLowerCase();
        if (!hay.includes(q)) return false;
      }
      for (const facet of facets) {
        const selected = facetValues[facet.key];
        if (!selected) continue;
        if (valueToText(item[facet.key]) !== selected) return false;
      }
      return true;
    });
  }, [facets, facetValues, items, query]);

  return (
    <section className="section-block">
      <header className="section-head">
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </header>

      <div className="toolbar">
        <label className="search-wrap">
          <span>Search</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Filter by name/id/text"
          />
        </label>

        {facets.map((facet) => (
          <label key={facet.key} className="facet-wrap">
            <span>{facet.label}</span>
            <select
              value={facetValues[facet.key] ?? ""}
              onChange={(event) =>
                setFacetValues((prev) => ({
                  ...prev,
                  [facet.key]: event.target.value,
                }))
              }
            >
              <option value="">All</option>
              {optionsByFacet[facet.key]?.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
        ))}
      </div>

      <p className="result-count">{filtered.length} result(s)</p>

      <div className="card-grid">
        {filtered.map((item, index) => {
          const id = valueToText(item.id) || `row-${index}`;
          const name = valueToText(item.name || item.title || item.id || "Unnamed");
          const description = snippet(
            item.description ?? item.summary ?? item.content ?? item.notes ?? item.title,
          );

          const chips: string[] = [];
          for (const facet of facets) {
            const value = valueToText(item[facet.key]);
            if (value) chips.push(`${facet.label}: ${value}`);
          }
          if (item.mode) chips.push(`Mode: ${valueToText(item.mode)}`);
          if (item.version) chips.push(`Version: ${valueToText(item.version)}`);
          if (item.analysis) chips.push("Analysis included");

          return (
            <article className="entity-card reveal" key={id}>
              <header>
                <h2>{name}</h2>
                <code>{id}</code>
              </header>
              {description && <p>{description}</p>}
              {chips.length > 0 && (
                <div className="chip-wrap">
                  {chips.slice(0, 4).map((chip) => (
                    <span key={`${id}-${chip}`} className="chip">
                      {chip}
                    </span>
                  ))}
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}
