import os
import datetime

def generate_sitemap_entries():
    base_url = "https://whik59140.github.io/links-italia"
    lists_dir = "lists"
    sitemap_entries = []

    # Main page entry
    sitemap_entries.append(f"""  <url>
    <loc>{base_url}/</loc>
    <lastmod>{datetime.date.today().isoformat()}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>""")

    # Entries for files in the lists directory
    if os.path.exists(lists_dir) and os.path.isdir(lists_dir):
        for filename in os.listdir(lists_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(lists_dir, filename)
                try:
                    # Get last modification time
                    mtime = os.path.getmtime(filepath)
                    lastmod_date = datetime.date.fromtimestamp(mtime).isoformat()
                except Exception:
                    # Fallback to today\'s date if mtime fails
                    lastmod_date = datetime.date.today().isoformat()
                
                # Ensure forward slashes for URL
                loc_path = f"{base_url}/{lists_dir}/{filename}".replace("\\\\", "/")

                sitemap_entries.append(f"""  <url>
    <loc>{loc_path}</loc>
    <lastmod>{lastmod_date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""")
    else:
        print(f"Warning: Directory \'{lists_dir}\' not found.")

    return sitemap_entries

def write_sitemap(entries):
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{os.linesep.join(entries)}
</urlset>
"""
    try:
        with open("sitemap.xml", "w", encoding="utf-8") as f:
            f.write(sitemap_content)
        print("sitemap.xml has been successfully updated.")
        # Verify by printing the first few lines of the generated sitemap
        if os.path.exists("sitemap.xml"):
            with open("sitemap.xml", "r", encoding="utf-8") as f_verify:
                print("\\nFirst 15 lines of generated sitemap.xml:")
                for _ in range(15):
                    line = f_verify.readline()
                    if not line:
                        break
                    print(line, end='')
    except IOError as e:
        print(f"Error writing sitemap.xml: {e}")

if __name__ == "__main__":
    generated_entries = generate_sitemap_entries()
    if generated_entries:
        write_sitemap(generated_entries)
    else:
        print("No sitemap entries were generated.") 