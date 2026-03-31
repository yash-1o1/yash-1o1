#!/usr/bin/env python3
"""
GitHub Profile Stats Generator
Inspired by Andrew6rant's profile README
"""

import os
import json
import datetime
from urllib import request

GITHUB_TOKEN = os.environ.get("GH_TOKEN", "")
USERNAME = "yash-1o1"

GRAPHQL_QUERY = """
{
  user(login: "%s") {
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      totalCount
      nodes {
        name
        stargazerCount
        primaryLanguage {
          name
        }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node {
              name
              color
            }
          }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
      }
    }
    followers {
      totalCount
    }
    following {
      totalCount
    }
    createdAt
  }
}
"""

def query_github(query):
    """Execute a GraphQL query against GitHub API."""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
    }
    data = json.dumps({"query": query}).encode("utf-8")
    req = request.Request("https://api.github.com/graphql", data=data, headers=headers)
    
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))

def calculate_stats():
    """Calculate all profile statistics."""
    result = query_github(GRAPHQL_QUERY % USERNAME)
    user = result["data"]["user"]
    
    repos = user["repositories"]["nodes"]
    total_repos = user["repositories"]["totalCount"]
    total_stars = sum(repo["stargazerCount"] for repo in repos)
    total_commits = user["contributionsCollection"]["totalCommitContributions"]
    total_contributions = user["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    followers = user["followers"]["totalCount"]
    following = user["following"]["totalCount"]
    
    # Calculate language stats
    language_sizes = {}
    for repo in repos:
        for edge in repo.get("languages", {}).get("edges", []):
            lang = edge["node"]["name"]
            size = edge["size"]
            color = edge["node"]["color"] or "#858585"
            if lang not in language_sizes:
                language_sizes[lang] = {"size": 0, "color": color}
            language_sizes[lang]["size"] += size
    
    # Sort by size
    sorted_langs = sorted(language_sizes.items(), key=lambda x: x[1]["size"], reverse=True)[:6]
    total_size = sum(lang[1]["size"] for lang in sorted_langs)
    
    languages = []
    for name, data in sorted_langs:
        percentage = (data["size"] / total_size * 100) if total_size > 0 else 0
        languages.append({
            "name": name,
            "percentage": round(percentage, 1),
            "color": data["color"]
        })
    
    # Account age
    created = datetime.datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00"))
    now = datetime.datetime.now(datetime.timezone.utc)
    years = (now - created).days // 365
    
    return {
        "repos": total_repos,
        "stars": total_stars,
        "commits": total_commits,
        "contributions": total_contributions,
        "followers": followers,
        "following": following,
        "years": years,
        "languages": languages,
        "updated": now.strftime("%Y-%m-%d %H:%M UTC")
    }

def generate_svg(stats, dark_mode=False):
    """Generate an SVG stats card."""
    bg_color = "#0d1117" if dark_mode else "#ffffff"
    text_color = "#c9d1d9" if dark_mode else "#24292f"
    secondary_color = "#8b949e" if dark_mode else "#57606a"
    border_color = "#30363d" if dark_mode else "#d0d7de"
    
    # Language bar
    lang_bar = ""
    offset = 0
    for lang in stats["languages"]:
        width = lang["percentage"] * 3.4  # Scale to 340px total
        lang_bar += f'<rect x="{30 + offset}" y="155" width="{width}" height="8" rx="2" fill="{lang["color"]}"/>'
        offset += width
    
    # Language legend
    lang_legend = ""
    for i, lang in enumerate(stats["languages"][:3]):
        y_pos = 180 + (i * 18)
        lang_legend += f'''
        <circle cx="35" cy="{y_pos}" r="5" fill="{lang["color"]}"/>
        <text x="45" y="{y_pos + 4}" fill="{text_color}" font-size="12">{lang["name"]} ({lang["percentage"]}%)</text>
        '''
    
    for i, lang in enumerate(stats["languages"][3:6]):
        y_pos = 180 + (i * 18)
        lang_legend += f'''
        <circle cx="200" cy="{y_pos}" r="5" fill="{lang["color"]}"/>
        <text x="210" y="{y_pos + 4}" fill="{text_color}" font-size="12">{lang["name"]} ({lang["percentage"]}%)</text>
        '''
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="250" viewBox="0 0 400 250">
  <rect width="400" height="250" rx="10" fill="{bg_color}" stroke="{border_color}" stroke-width="1"/>
  
  <text x="30" y="35" fill="{text_color}" font-size="18" font-weight="600" font-family="Segoe UI, sans-serif">Yash's GitHub Stats</text>
  <text x="30" y="55" fill="{secondary_color}" font-size="11" font-family="Segoe UI, sans-serif">Updated: {stats["updated"]}</text>
  
  <text x="30" y="85" fill="{text_color}" font-size="13" font-family="Segoe UI, sans-serif">
    <tspan font-weight="600">{stats["repos"]}</tspan> repositories
  </text>
  <text x="200" y="85" fill="{text_color}" font-size="13" font-family="Segoe UI, sans-serif">
    <tspan font-weight="600">{stats["stars"]}</tspan> stars earned
  </text>
  
  <text x="30" y="108" fill="{text_color}" font-size="13" font-family="Segoe UI, sans-serif">
    <tspan font-weight="600">{stats["commits"]}</tspan> commits (this year)
  </text>
  <text x="200" y="108" fill="{text_color}" font-size="13" font-family="Segoe UI, sans-serif">
    <tspan font-weight="600">{stats["contributions"]}</tspan> contributions
  </text>
  
  <text x="30" y="131" fill="{text_color}" font-size="13" font-family="Segoe UI, sans-serif">
    <tspan font-weight="600">{stats["followers"]}</tspan> followers
  </text>
  <text x="200" y="131" fill="{text_color}" font-size="13" font-family="Segoe UI, sans-serif">
    <tspan font-weight="600">{stats["years"]}</tspan> years on GitHub
  </text>
  
  {lang_bar}
  {lang_legend}
</svg>'''
    
    return svg

def main():
    print("Fetching GitHub stats...")
    stats = calculate_stats()
    
    print(f"Stats: {stats['repos']} repos, {stats['commits']} commits, {stats['stars']} stars")
    
    # Generate both dark and light mode SVGs
    dark_svg = generate_svg(stats, dark_mode=True)
    light_svg = generate_svg(stats, dark_mode=False)
    
    with open("dark_mode.svg", "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print("Generated dark_mode.svg")
    
    with open("light_mode.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    print("Generated light_mode.svg")
    
    # Save stats cache
    with open("cache/stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print("Saved stats to cache/stats.json")

if __name__ == "__main__":
    main()
