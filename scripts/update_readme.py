#!/usr/bin/env python3
"""
GitHub Profile README Generator

This script analyzes a GitHub user's repositories and generates a README.md file
with technology stack information, repository statistics, and contribution data.
"""
import os
import re
import json
import requests
from github import Github
from collections import Counter
from datetime import datetime

# Configuration
# Try to get username from environment variables if running in GitHub Actions
USERNAME = os.getenv("GITHUB_REPOSITORY", "").split("/")[0]
# If not found, use a default username for local testing
if not USERNAME:
    try:
        # Try to get username from the GitHub context if available
        github_event_path = os.getenv("GITHUB_EVENT_PATH", "")
        if github_event_path and os.path.exists(github_event_path):
            with open(github_event_path, "r") as f:
                event = json.load(f)
                USERNAME = event.get("repository", {}).get("owner", {}).get("login", "")
        # If still no username, use a default
        if not USERNAME:
            USERNAME = "Tibutti"  # Default to the GitHub account Tibutti
    except (json.JSONDecodeError, FileNotFoundError):
        USERNAME = "Tibutti"  # Default fallback

# Get GitHub token from environment variables
TOKEN = os.getenv("GITHUB_TOKEN")
API_URL = "https://api.github.com"
EXCLUDE_REPOS = [""]  # Add repository names to exclude
EXCLUDE_LANGS = [""]  # Add languages to exclude from the analysis
MAX_LANG_DISPLAY = 15  # Maximum number of languages to display

# Check if we're in test mode (no GitHub token)
TEST_MODE = TOKEN is None

# Initialize GitHub API client if token is available
# g will be used only after we check for TEST_MODE, so even if it's None, 
# we'll avoid calling methods on it
g = None
if not TEST_MODE:
    try:
        g = Github(TOKEN)
    except Exception as e:
        print(f"Error initializing GitHub client: {e}")
        TEST_MODE = True  # Force test mode if client initialization fails

def get_language_badge(lang):
    """Generate a badge for a programming language using shields.io"""
    # Dictionary mapping language names to shield styles and colors
    lang_style = {
        "Python": {"logo": "python", "color": "3776AB"},
        "JavaScript": {"logo": "javascript", "color": "F7DF1E", "logoColor": "black"},
        "TypeScript": {"logo": "typescript", "color": "3178C6"},
        "HTML": {"logo": "html5", "color": "E34F26"},
        "CSS": {"logo": "css3", "color": "1572B6"},
        "Java": {"logo": "java", "color": "007396"},
        "C#": {"logo": "csharp", "color": "239120"},
        "C++": {"logo": "cplusplus", "color": "00599C"},
        "PHP": {"logo": "php", "color": "777BB4"},
        "Ruby": {"logo": "ruby", "color": "CC342D"},
        "Swift": {"logo": "swift", "color": "FA7343"},
        "Go": {"logo": "go", "color": "00ADD8"},
        "Rust": {"logo": "rust", "color": "000000"},
        "Kotlin": {"logo": "kotlin", "color": "0095D5"},
        "Dart": {"logo": "dart", "color": "0175C2"},
        "Shell": {"logo": "gnubash", "color": "4EAA25"},
        "Jupyter Notebook": {"logo": "jupyter", "color": "F37626"},
        "R": {"logo": "r", "color": "276DC3"},
        "Vue": {"logo": "vuedotjs", "color": "4FC08D"},
        "React": {"logo": "react", "color": "61DAFB", "logoColor": "black"},
        "Angular": {"logo": "angular", "color": "DD0031"},
        "Django": {"logo": "django", "color": "092E20"},
        "Flask": {"logo": "flask", "color": "000000"},
        "Node.js": {"logo": "nodedotjs", "color": "339933"},
        "Express": {"logo": "express", "color": "000000"},
    }
    
    # Normalize language name
    norm_lang = lang.replace(" ", "").lower()
    
    # Check if we have a specific style for this language
    style = lang_style.get(lang, {})
    
    logo = style.get("logo", norm_lang)
    color = style.get("color", "007ec6")
    logo_color = style.get("logoColor", "white")
    
    badge_url = f"https://img.shields.io/badge/{lang}-{color}?style=for-the-badge&logo={logo}&logoColor={logo_color}"
    return f"![{lang}]({badge_url})"

def get_tool_badge(tool, category=None):
    """Generate badges for development tools and frameworks"""
    tool_style = {
        "Git": {"logo": "git", "color": "F05032"},
        "GitHub": {"logo": "github", "color": "181717"},
        "GitLab": {"logo": "gitlab", "color": "FCA121"},
        "Docker": {"logo": "docker", "color": "2496ED"},
        "Kubernetes": {"logo": "kubernetes", "color": "326CE5"},
        "VS Code": {"logo": "visualstudiocode", "color": "007ACC"},
        "IntelliJ IDEA": {"logo": "intellijidea", "color": "000000"},
        "PyCharm": {"logo": "pycharm", "color": "000000"},
        "npm": {"logo": "npm", "color": "CB3837"},
        "Yarn": {"logo": "yarn", "color": "2C8EBB"},
        "AWS": {"logo": "amazonaws", "color": "232F3E"},
        "Azure": {"logo": "microsoftazure", "color": "0078D4"},
        "GCP": {"logo": "googlecloud", "color": "4285F4"},
        "Heroku": {"logo": "heroku", "color": "430098"},
        "Netlify": {"logo": "netlify", "color": "00C7B7"},
        "Vercel": {"logo": "vercel", "color": "000000"},
        "PostgreSQL": {"logo": "postgresql", "color": "336791"},
        "MySQL": {"logo": "mysql", "color": "4479A1"},
        "MongoDB": {"logo": "mongodb", "color": "47A248"},
        "Redis": {"logo": "redis", "color": "DC382D"},
        "SQLite": {"logo": "sqlite", "color": "003B57"},
    }
    
    style = tool_style.get(tool, {})
    logo = style.get("logo", tool.lower().replace(" ", ""))
    color = style.get("color", "007ec6")
    
    badge_url = f"https://img.shields.io/badge/{tool.replace(' ', '%20')}-{color}?style=for-the-badge&logo={logo}"
    return f"![{tool}]({badge_url})"

def get_sample_repo_data():
    """Get sample repository data for testing without GitHub API"""
    # Sample language data (language name, bytes of code)
    sample_languages = [
        ("Python", 50000),
        ("JavaScript", 30000),
        ("HTML", 10000),
        ("CSS", 8000),
        ("TypeScript", 5000),
        ("Java", 3000)
    ]
    
    # Sample tools and frameworks
    sample_tools = ["Git", "Docker", "VS Code", "GitHub Actions", "AWS"]
    sample_frameworks = ["React", "Django", "Flask", "Node.js", "Express"]
    
    # Sample repository stats
    sample_stats = {
        "total_repos": 12,
        "total_stars": 48,
        "total_forks": 15
    }
    
    # Sample project categories
    sample_project_categories = {
        "Web Development": 5,
        "Data Science": 3,
        "Mobile Apps": 2,
        "Automation": 2
    }
    
    # Sample focused topics
    sample_topics = ["web-app", "data-analysis", "api", "automation", "mobile"]
    
    return {
        "languages": sample_languages,
        "tools": sample_tools,
        "frameworks": sample_frameworks,
        "stats": sample_stats,
        "project_categories": sample_project_categories,
        "topics": sample_topics
    }

def analyze_repositories():
    """Analyze repositories to determine the technology stack"""
    # Use sample data when in test mode
    if TEST_MODE or g is None:
        print("Running in test mode with sample data")
        return get_sample_repo_data()
    
    # Real analysis using GitHub API
    try:
        user = g.get_user(USERNAME)
        
        # Get repositories
        repos = user.get_repos()
        
        # Collect repository languages
        lang_stats = Counter()
        tools_detected = set()
        frameworks_detected = set()
        
        # Project categories and topics
        project_categories = Counter()
        topics_counter = Counter()
        
        # Repository statistics
        total_stars = 0
        total_forks = 0
        total_repos = 0
        
        # Category detection keywords
        category_keywords = {
            "Web Development": ["web", "website", "frontend", "backend", "fullstack", "react", "vue", "angular", "node", "express", "django", "flask", "html", "css", "javascript"],
            "Data Science": ["data", "analysis", "analytics", "visualization", "machine learning", "ml", "ai", "artificial intelligence", "pandas", "numpy", "jupyter", "tensorflow", "pytorch"],
            "Mobile Apps": ["mobile", "android", "ios", "app", "flutter", "react native", "swift", "kotlin"],
            "Desktop Applications": ["desktop", "gui", "ui", "electron", "qt", "gtk", "wxwidgets"],
            "DevOps": ["devops", "ci/cd", "pipeline", "automation", "kubernetes", "docker", "container", "jenkins", "github actions"],
            "Game Development": ["game", "unity", "unreal", "godot", "pygame"],
            "IoT": ["iot", "internet of things", "raspberry pi", "arduino", "embedded"],
            "Blockchain": ["blockchain", "crypto", "web3", "ethereum", "smart contract", "solidity"],
            "API": ["api", "rest", "graphql", "microservice"],
            "Security": ["security", "cybersecurity", "encryption", "authentication", "authorization"],
            "Automation": ["automation", "bot", "script", "scraper", "crawler"],
            "Education": ["education", "learning", "tutorial", "course"],
            "Documentation": ["documentation", "docs", "wiki"],
            "Open Source": ["open source", "community", "contribution"]
        }
        
        for repo in repos:
            if repo.name in EXCLUDE_REPOS or repo.fork:
                continue
            
            total_repos += 1
            total_stars += repo.stargazers_count
            total_forks += repo.forks_count
            
            # Get languages used in this repository
            languages = repo.get_languages()
            for lang, bytes_count in languages.items():
                if lang not in EXCLUDE_LANGS:
                    lang_stats[lang] += bytes_count
            
            # Get topics from repository
            repo_topics = repo.get_topics()
            for topic in repo_topics:
                topics_counter[topic] += 1
            
            # Check README and description for tools/frameworks and categories
            try:
                readme_content = repo.get_readme().decoded_content.decode('utf-8').lower()
                description = (repo.description or "").lower()
                repo_name = repo.name.lower()
                
                # Combine all text data for category analysis
                all_text = f"{description} {readme_content} {repo_name} {' '.join(repo_topics)}"
                
                # Detect project categories
                for category, keywords in category_keywords.items():
                    for keyword in keywords:
                        if keyword in all_text:
                            project_categories[category] += 1
                            break
                
                # Check for common frameworks and tools in README and description
                for keyword, category in [
                    ("docker", "tools"),
                    ("kubernetes", "tools"),
                    ("django", "frameworks"),
                    ("flask", "frameworks"),
                    ("react", "frameworks"),
                    ("vue", "frameworks"),
                    ("angular", "frameworks"),
                    ("node", "frameworks"),
                    ("express", "frameworks"),
                    ("aws", "tools"),
                    ("azure", "tools"),
                    ("gcp", "tools"),
                    ("terraform", "tools"),
                    ("ansible", "tools"),
                    ("jenkins", "tools"),
                    ("github actions", "tools"),
                    ("postgresql", "databases"),
                    ("mysql", "databases"),
                    ("mongodb", "databases"),
                    ("redis", "databases"),
                    ("sqlite", "databases")
                ]:
                    if keyword in readme_content or keyword in description:
                        if category == "tools":
                            tools_detected.add(keyword.title())
                        else:
                            frameworks_detected.add(keyword.title())
            except Exception as e:
                # Skip if README can't be fetched
                print(f"Error processing repo {repo.name}: {e}")
                pass
            
        # Sort languages by usage
        top_languages = sorted(lang_stats.items(), key=lambda x: x[1], reverse=True)
        
        # Get most common project categories
        top_categories = dict(project_categories.most_common(5))
        
        # Get most common topics
        top_topics = [topic for topic, count in topics_counter.most_common(8)]
        
        return {
            "languages": top_languages[:MAX_LANG_DISPLAY],
            "tools": sorted(list(tools_detected)),
            "frameworks": sorted(list(frameworks_detected)),
            "project_categories": top_categories,
            "topics": top_topics,
            "stats": {
                "total_repos": total_repos,
                "total_stars": total_stars,
                "total_forks": total_forks
            }
        }
    except Exception as e:
        print(f"Error accessing GitHub API: {e}")
        # Return sample data as fallback
        print("Falling back to sample data")
        return get_sample_repo_data()

def get_sample_user_stats():
    """Get sample user statistics for testing"""
    return {
        "public_repos": 15,
        "followers": 45,
        "following": 32,
        "created_at": "2020-01-01T00:00:00Z"
    }

def get_contribution_stats():
    """Get contribution statistics for the user"""
    # Use sample data in test mode
    if TEST_MODE:
        print("Using sample user statistics")
        return get_sample_user_stats()
    
    try:
        # Use GitHub API to get contribution data
        headers = {'Authorization': f'token {TOKEN}'} if TOKEN else {}
        
        # Get user information
        response = requests.get(f"{API_URL}/users/{USERNAME}", headers=headers)
        
        if response.status_code != 200:
            print(f"API error: {response.status_code}")
            return get_sample_user_stats()
            
        user_data = response.json()
        
        # We can't directly get contribution count from API, but we can note account creation date
        created_at = user_data.get('created_at', '')
        
        return {
            "public_repos": user_data.get('public_repos', 0),
            "followers": user_data.get('followers', 0),
            "following": user_data.get('following', 0),
            "created_at": created_at
        }
    except Exception as e:
        print(f"Error accessing GitHub API for user stats: {e}")
        return get_sample_user_stats()

def generate_readme(analysis, stats):
    """Generate the README.md content"""
    now = datetime.now()
    
    # Introduction with animated header based on top category
    def get_category_animation(categories):
        """Get animated SVG header based on top project category"""
        if not categories:
            return """<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=24&duration=4000&pause=1000&color=36BCF7FF&center=true&width=600&background=00000000&lines=Welcome+to+my+GitHub+Profile;I'm+a+Developer;Passionate+about+coding;Creating+innovative+solutions" alt="Typing SVG" />
</div>"""
        
        # Get top category
        top_category = list(categories.keys())[0] if categories else "Web Development"
        
        # Generate custom typing animation with category
        return f"""<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=24&duration=4000&pause=1000&color=36BCF7FF&center=true&width=600&background=00000000&lines=Welcome+to+my+GitHub+Profile;I'm+a+{top_category.replace(' ', '+')}+Developer;Passionate+about+coding;Building+{top_category.replace(' ', '+')}+solutions" alt="Typing SVG" />
</div>"""
    
    # Get header with animated typing
    category_header = get_category_animation(analysis.get("project_categories", {}))
    
    readme = f"""
{category_header}

# Hi there 👋, I'm {USERNAME}

This is my automatically updated GitHub profile that shows my tech stack based on my repository activity.

"""
    
    # Add project focus section if categories are available
    if "project_categories" in analysis and analysis["project_categories"]:
        readme += "## 🚀 What I Work On\n\n"
        readme += "My GitHub repositories focus on these areas:\n\n"
        
        # Add bullet points for each project category with count
        for category, count in analysis["project_categories"].items():
            readme += f"- **{category}** ({count} repos)\n"
        
        # Add common topics/tags if available
        if "topics" in analysis and analysis["topics"]:
            readme += "\n**Common topics:** "
            for topic in analysis["topics"]:
                readme += f"`#{topic}` "
        
        readme += "\n"
    
    # Tech stack section with animated separator
    readme += """
## 🛠️ My Tech Stack

<div align="center">
  <img src="https://i.imgur.com/KXx0cCx.gif" width="600" height="4" alt="animated tech line">
</div>

### Languages I Use
    
"""
    # Add language badges
    for lang, bytes_count in analysis["languages"]:
        readme += f"{get_language_badge(lang)} "
    
    # Add frameworks if detected
    if analysis["frameworks"]:
        readme += "\n\n### Frameworks & Libraries\n\n"
        for framework in analysis["frameworks"]:
            readme += f"{get_tool_badge(framework)} "
    
    # Add tools if detected
    if analysis["tools"]:
        readme += "\n\n### Tools & Technologies\n\n"
        for tool in analysis["tools"]:
            readme += f"{get_tool_badge(tool)} "
    
    # Add statistics with animated elements
    readme += f"""

## 📊 GitHub Stats

<div align="center">
  <table>
    <tr>
      <td><b>🔭 Repositories</b></td>
      <td><b>⭐ Stars</b></td>
      <td><b>🍴 Forks</b></td>
      <td><b>👥 Followers</b></td>
    </tr>
    <tr>
      <td><img alt="Repositories" src="https://img.shields.io/badge/{analysis["stats"]["total_repos"]}-4c71f2?style=for-the-badge&logo=github&logoColor=white"/></td>
      <td><img alt="Stars" src="https://img.shields.io/badge/{analysis["stats"]["total_stars"]}-FFD700?style=for-the-badge&logo=github&logoColor=white"/></td>
      <td><img alt="Forks" src="https://img.shields.io/badge/{analysis["stats"]["total_forks"]}-4c71f2?style=for-the-badge&logo=github&logoColor=white"/></td>
      <td><img alt="Followers" src="https://img.shields.io/badge/{stats["followers"]}-FFD700?style=for-the-badge&logo=github&logoColor=white"/></td>
    </tr>
  </table>
</div>

<div align="center">
  <img src="https://github-readme-stats.vercel.app/api?username={USERNAME}&show_icons=true&theme=radical" alt="GitHub stats" />
</div>

<div align="center">
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username={USERNAME}&layout=compact&theme=radical" alt="Top Languages" />
</div>

## 📈 Activity

<div align="center">
  <img src="https://github-profile-trophy.vercel.app/?username={USERNAME}&theme=radical&row=1&column=6" alt="GitHub trophies" />
</div>

<div align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username={USERNAME}&theme=github" alt="GitHub Activity Graph" />
</div>

---

<details>
<summary>⚡ More Stats</summary>
<br>

![Profile Details](https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username={USERNAME}&theme=monokai)

![Streak Stats](https://github-readme-streak-stats.herokuapp.com/?user={USERNAME}&theme=dark)

</details>

---

<div align="center">
  <img src="https://i.imgur.com/KXx0cCx.gif" width="600" height="4" alt="animated footer line">
  <br>
  <img src="https://komarev.com/ghpvc/?username={USERNAME}&label=Profile+Views" alt="Profile views">
  <br>
  <i>This profile README is automatically updated using GitHub Actions.<br>Last updated: {now.strftime("%Y-%m-%d")}</i>
</div>
"""
    return readme

def main():
    """Main function to update the README"""
    # Get repository analysis
    analysis = analyze_repositories()
    
    # Get contribution stats
    stats = get_contribution_stats()
    
    # Generate README content
    readme_content = generate_readme(analysis, stats)
    
    # Write to README.md
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print(f"README.md updated successfully for {USERNAME}")

if __name__ == "__main__":
    main()
