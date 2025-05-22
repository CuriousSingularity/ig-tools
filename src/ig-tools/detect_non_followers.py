import argparse
import re
import time
import difflib
import webbrowser


def extract_links(html_content):
    """Extracts all href links from a given HTML content."""
    return re.findall(r'href="(https?://[^"]+)"', html_content)


def clean_html(html_content):
    """Removes HTML tags and extra whitespace."""
    clean_text = re.sub(r"<[^>]+>", "", html_content)
    return re.sub(r"\s+", " ", clean_text).strip()


def find_and_extract_diff_links(followers, followings):
    """
    Finds the differences between two HTML documents, extracts links from the differences,
    and returns a clean list of new links in followers compared to followings.
    """
    diff = difflib.unified_diff(
        followings.splitlines(keepends=True), followers.splitlines(keepends=True)
    )
    diff_content = "".join(list(diff))
    extracted_links = extract_links(diff_content)
    new_instagram_links = []
    for link in extracted_links:
        if "https://www.instagram.com/" in link and link not in extract_links(
            followings
        ):
            new_instagram_links.append(link)
    return new_instagram_links


def main(args):
    """
    Main function to identify and open Instagram users who do not follow back.

    Args:
        args: An object with the following attributes:
            - followers (str): Path to the HTML file containing the list of followers.
            - followings (str): Path to the HTML file containing the list of followings.
            - num_tabs (int): Number of browser tabs to open simultaneously.
            - duration (int or float): Time in seconds to wait between opening batches of tabs.

    Behavior:
        - Reads the followers and followings HTML files.
        - Extracts the list of users who are followed but do not follow back.
        - Prints the number of non-followers found.
        - Opens the Instagram profiles of non-followers in the browser, in batches defined by num_tabs, pausing for duration seconds between batches.
        - If either file is missing, prints an error message and exits.
        - If no non-followers are found, prints a corresponding message.
    """

    followers_file = args.followers
    followings_file = args.followings
    num_tabs = args.num_tabs
    duration = args.duration

    if not followers_file or not followings_file:
        print("Please provide both followers and followings HTML files.")
        return

    with open(args.followers, "r", encoding="utf-8") as f:
        followers = f.read()
    with open(args.followings, "r", encoding="utf-8") as f:
        followings = f.read()

    new_links = find_and_extract_diff_links(followings, followers)
    print(f"Number of non-followers found: {len(new_links)}")

    if new_links:
        for index in range(0, len(new_links), num_tabs):
            print("Opening new links in chunks of", index)
            for i in range(index, index + num_tabs):
                if i < len(new_links):
                    print(new_links[i])
                    webbrowser.open_new_tab(new_links[i])
            time.sleep(duration)
    else:
        print("No new Instagram links were found in Followers compared to Followings.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find Instagram accounts that are not followed back.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--followers", "-fw", help="Path to the followers HTML document"
    )
    parser.add_argument(
        "--followings", "-fg", help="Path to the followings HTML document"
    )
    parser.add_argument(
        "--num-tabs", "-t", type=int, default=5, help="Number of tabs to open at once"
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=30,
        help="Time to wait between opening tabs (in seconds)",
    )
    args = parser.parse_args()
    main(args)
