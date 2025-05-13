import requests
import xml.etree.ElementTree as ET
from typing import Set, List
import os
import datetime # For timestamp if needed, though less critical for batch files

def get_sitemap_urls(sitemap_url: str, all_urls: Set[str], processed_sitemaps: Set[str]) -> None:
    '''
    Recursively fetches and parses sitemaps to extract all unique URLs.
    '''
    if sitemap_url in processed_sitemaps:
        print(f"Skipping already processed sitemap: {sitemap_url}")
        return

    print(f"Processing sitemap: {sitemap_url}")
    processed_sitemaps.add(sitemap_url)

    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sitemap {sitemap_url}: {e}")
        return

    try:
        namespaces = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        content = response.content.strip()
        if not content:
            print(f"Sitemap is empty: {sitemap_url}")
            return
        root = ET.fromstring(content)
        loc_elements = root.findall('.//sitemap:loc', namespaces)
        if not loc_elements:
            loc_elements = root.findall('.//loc')

        for loc_element in loc_elements:
            if loc_element.text:
                url = loc_element.text.strip()
                if url.endswith('.xml'):
                    get_sitemap_urls(url, all_urls, processed_sitemaps)
                else:
                    all_urls.add(url)
    except ET.ParseError as e:
        print(f"Error parsing XML from {sitemap_url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {sitemap_url}: {e}")

if __name__ == "__main__":
    initial_sitemap_url = "https://www.incontri-italia.it/sitemap.xml"
    
    # --- Configuration for Batched Output for GitHub Pages ---
    output_base_dir = "incontri-italia-link-showcase" # Main directory for the repo content
    lists_subdir = "lists"  # Subdirectory for batched link files
    batch_size = 75      # Number of URLs per batch file (e.g., 50-100)
    readme_filename = "README.md" # Main index file for the repo
    # ----

    # Create base directory and lists subdirectory if they don't exist
    full_lists_path = os.path.join(output_base_dir, lists_subdir)
    os.makedirs(full_lists_path, exist_ok=True)
    print(f"Output directory structure will be created in: {os.path.abspath(output_base_dir)}")

    extracted_urls: Set[str] = set()
    processed_sitemap_links: Set[str] = set()

    print(f"Starting extraction from: {initial_sitemap_url}")
    get_sitemap_urls(initial_sitemap_url, extracted_urls, processed_sitemap_links)
    print(f"\nExtraction complete. Found {len(extracted_urls)} unique URLs.")

    if not extracted_urls:
        print("No URLs were extracted. Halting further processing.")
    else:
        sorted_urls = sorted(list(extracted_urls))
        batch_files_details = [] # To store (display_name, relative_path) for README
        num_batches = (len(sorted_urls) + batch_size - 1) // batch_size

        print(f"Preparing to write URLs into {num_batches} batch files...")

        for i in range(num_batches):
            batch_start_index = i * batch_size
            batch_end_index = batch_start_index + batch_size
            current_batch_urls = sorted_urls[batch_start_index:batch_end_index]
            
            batch_file_number = i + 1
            # Pad with leading zeros for consistent sorting if many files (e.g., 001, 002, ... 010, 011)
            batch_filename = f"list-{batch_file_number:03d}.md" 
            batch_filepath = os.path.join(full_lists_path, batch_filename)
            
            # Store relative path for the main README.md
            relative_batch_path = os.path.join(lists_subdir, batch_filename).replace('\\', '/') # Ensure forward slashes for MD links
            batch_display_name = f"Link Batch {batch_file_number:03d}"
            batch_files_details.append((batch_display_name, relative_batch_path))

            with open(batch_filepath, 'w', encoding='utf-8') as bf:
                bf.write(f"# Incontri Italia - Link Batch {batch_file_number:03d}\n\n")
                bf.write(f"This file contains a curated selection of pages from [incontri-italia.it](https://www.incontri-italia.it/), part of a larger collection.\n\n")
                bf.write(f"See the [main index](../../{readme_filename}) for a full list of batches.\n\n") # Link back to main README
                bf.write("## Links in this Batch\n\n")
                for url in current_batch_urls:
                    link_text = url.split('//')[-1] # Basic link text
                    bf.write(f"- [{link_text}]({url})\n")
            print(f"Successfully wrote {len(current_batch_urls)} URLs to {batch_filepath}")

        # --- Create the main README.md ---
        readme_filepath = os.path.join(output_base_dir, readme_filename)
        print(f"\nCreating main {readme_filename} at {readme_filepath}...")
        current_time_for_readme = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(readme_filepath, 'w', encoding='utf-8') as rf:
            rf.write("# Incontri Italia - Curated Link Showcase\n\n") # Main Title
            rf.write(f"**Last Updated:** {current_time_for_readme}\n")
            rf.write(f"**Source Sitemap:** [{initial_sitemap_url}]({initial_sitemap_url})\n\n")
            
            rf.write("## Welcome!\n\n") # Placeholder for your Introduction
            rf.write("This repository organizes key pages and resources from [incontri-italia.it](https://www.incontri-italia.it/), presented in manageable batches to aid in discovery and navigation. "
                     "Our platform, Incontri Italia, is dedicated to [Your Site's Main Purpose - e.g., fostering connections across Italy]. "
                     "We offer [Briefly describe services - e.g., user profiles, classifieds] to help you connect.\n\n")
            rf.write("Please replace the placeholder text above with your detailed website description!\n\n")

            rf.write("## Explore Our Link Collections\n\n")
            rf.write("Below is a directory of Markdown files, each containing a batch of URLs from our website:\n\n")
            if batch_files_details:
                for display_name, path_to_file in batch_files_details:
                    rf.write(f"- [{display_name}]({path_to_file})\n")
            else:
                rf.write("No link batches were generated.\n")
            
            rf.write("\n## About This Repository\n\n") # Placeholder for more context
            rf.write("This collection is provided to enhance the visibility and accessibility of content from incontri-italia.it. "
                     "It can be useful for archival purposes and for search engines to better understand our site structure.\n\n")

            rf.write("---\n\n") # Footer / Call to Action
            rf.write("For the complete and most up-to-date experience, please visit our main website: **[incontri-italia.it](https://www.incontri-italia.it/)**\n")

        print(f"Successfully created {readme_filename} with links to {len(batch_files_details)} batch files.")
        print(f"\nTotal unique URLs processed: {len(sorted_urls)}")
        print(f"Total sitemaps processed: {len(processed_sitemap_links)}")
        print(f"Output generated in directory: {os.path.abspath(output_base_dir)}")
        print("\nNext Steps for GitHub Pages:")
        print(f"1. Review the generated files in the '{output_base_dir}' directory.")
        print(f"2. **Crucially, customize the main {readme_filename}** (especially the 'Welcome!' section) with your detailed website description using the prompts we discussed.")
        print("3. Create a new public GitHub repository (e.g., name it 'incontri-italia-link-showcase').")
        print(f"4. Upload the entire contents of the '{output_base_dir}' directory (including the '{readme_filename}' and the 'lists/' subdirectory) to this new GitHub repository.")
        print("5. Enable GitHub Pages for this repository (Settings -> Pages). ")
        print("6. Submit your GitHub Pages site URL to Google Search Console and Bing Webmaster Tools.") 