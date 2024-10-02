# -*- coding: utf-8-sig -*-
import csv
import time
import pycountry
from bs4 import BeautifulSoup, Comment
from collections import defaultdict
from playwright.async_api import async_playwright
import os
from playwright_stealth import stealth_async  # Import stealth async method from stealth plugin
import asyncio

#Note: Add the letters you want to scrape to the following list 'aa','ab',...etc
players = ['ea','eb','ec', 'ed', 'ee','ef' ,'eg','eh', 'ei','ej','ek','el', 'em','en','ep','eq','er', 'es', 'et','eu','ev', 'ew', 'ex', 'ey','ez', 'fa','fd', 'fi', 'fj','fl', 'fo','fr','ft','fu','fy']
# URL of the player's page

# Function to get the full country name from a 2-letter code
def get_full_country_name(country_code):
    try:
        country = pycountry.countries.get(alpha_2=country_code.upper())
        if country:
            return country.name
    except KeyError:
        pass  # Handle cases where country is not found
    return country_code  # Fallback to country code if name not found

# Function to get clubs the player played for
def get_clubs(soup):
    try:
        stats_table = soup.find('table', {'id': 'stats_misc_dom_lg'})
        clubs_in_order = []
        seen_clubs = set()

        if stats_table:
            rows = stats_table.find_all('tr', {'id': 'stats'})
            for row in rows:
                club_cell = row.find('td', {'data-stat': 'team'})
                if club_cell:
                    club = club_cell.get_text(strip=True)
                    if club not in seen_clubs:
                        clubs_in_order.append(club)
                        seen_clubs.add(club)
        return " ~ ".join(clubs_in_order)
    except Exception as e:
        print(f"Error getting clubs: {e}")
        return ""

# Function to get trophies won by the player
def get_trophies_won(soup):
    try:
        stats_table = soup.find('table', {'id': 'stats_misc_dom_lg'})
        trophies = {}

        if stats_table:
            rows = stats_table.find_all('tr', {'id': 'stats'})
            for row in rows:
                competition = row.find('td', {'data-stat': 'comp_level'})
                rank = row.find('td', {'data-stat': 'lg_finish'})
                if competition and rank:
                    comp_name = competition.get_text(strip=True)

                    rank_value = rank.get_text(strip=True)
                    if rank_value == '1st' or rank_value == 'W':
                        if comp_name in trophies:
                            trophies[comp_name] += 1
                        else:
                            trophies[comp_name] = 1
        return " ~ ".join([f"{comp_name[2:]} ({count})" if count > 1 else comp_name[2:] for comp_name, count in trophies.items()])
    except Exception as e:
        print(f"Error getting trophies: {e}")
        return ""

# Function to get personal awards
def get_personal_awards(soup):
    try:
        awards = []
        element = soup.find('div', class_='leaderboard_wrapper', id='all_leaders')
        if element:
            comments = soup.find_all(string=lambda text: isinstance(text, Comment))
            for comment in comments:
                comment_soup = BeautifulSoup(comment, 'html.parser')
                sections = ['leaders_award_global', 'leaders_award_continental', 'leaders_award_national', 'leaders_award_league']
                for section in sections:
                    section_div = comment_soup.find('div', {'id': section})
                    if section_div:
                        awards.extend([award.get_text(strip=True) for award in section_div.find_all('td', class_='single')])
        return " ~ ".join(awards)
    except Exception as e:
        print(f"Error getting awards: {e}")
        return ""

# Function to get domestic cup trophies
def get_domestic_cup_trophies(soup):
    try:
        stats_table = soup.find('table', {'id': 'stats_misc_dom_cup'})
        competition_wins = defaultdict(int)

        if stats_table:
            rows = stats_table.find_all('tr', {'id': 'stats'})
            for row in rows:
                competition = row.find('td', {'data-stat': 'comp_level'})
                league_finish = row.find('td', {'data-stat': 'lg_finish'})
                if competition and league_finish:
                    comp_name = competition.get_text(strip=True)
                    if comp_name[0] == '1' and comp_name[1] == '.':
                        comp_name = comp_name[2:]
                    finish_position = league_finish.get_text(strip=True)
                    if finish_position == '1st' or finish_position == 'W':
                        competition_wins[comp_name] += 1
        return " ~ ".join([f"{comp_name} ({count})" if count > 1 else comp_name for comp_name, count in competition_wins.items()])
    except Exception as e:
        print(f"Error getting domestic cup trophies: {e}")
        return ""

# Function to get international cup trophies
def get_international_cup_trophies(soup):
    try:
        stats_table = soup.find('table', {'id': 'stats_misc_intl_cup'})
        competition_wins = defaultdict(int)

        if stats_table:
            rows = stats_table.find_all('tr', {'id': 'stats'})
            for row in rows:
                competition = row.find('td', {'data-stat': 'comp_level'})
                league_finish = row.find('td', {'data-stat': 'lg_finish'})
                if competition and league_finish:
                    comp_name = competition.get_text(strip=True)
                    if comp_name[0] == '1' and comp_name[1] == '.':
                        comp_name = comp_name[2:]
                    finish_position = league_finish.get_text(strip=True)
                    if finish_position == '1st' or finish_position == 'W':
                        competition_wins[comp_name] += 1
        return " ~ ".join([f"{comp_name} ({count})" if count > 1 else comp_name for comp_name, count in competition_wins.items()])
    except Exception as e:
        print(f"Error getting international cup trophies: {e}")
        return ""

# Function to get national team trophies
def get_national_team_trophies(soup):
    try:
        stats_table = soup.find('table', {'id': 'stats_misc_nat_tm'})
        competition_wins = defaultdict(int)

        if stats_table:
            rows = stats_table.find_all('tr', {'id': 'stats'})
            for row in rows:
                competition = row.find('td', {'data-stat': 'comp_level'})
                league_finish = row.find('td', {'data-stat': 'lg_finish'})
                if competition and league_finish:
                    comp_name = competition.get_text(strip=True)
                    if comp_name[0] == '1' and comp_name[1] == '.':
                        comp_name = comp_name[2:]                    

                    finish_position = league_finish.get_text(strip=True)
                    if finish_position == '1st' or finish_position == 'W' or finish_position == 'F':
                        competition_wins[comp_name] += 1
        return " ~ ".join([f"{comp_name} ({count})" if count > 1 else comp_name for comp_name, count in competition_wins.items()])
    except Exception as e:
        print(f"Error getting national team trophies: {e}")
        return ""

def get_player_info(soup):
    # Step 1: Find the div with id="info"
    info_div = soup.find('div', id="info")

    if info_div:
        # Step 2: Find the div with id="meta" inside info
        meta_div = info_div.find('div', id="meta")
        
        if meta_div:
            # Step 3: Find the h1 tag (which contains the player's name) directly inside meta
            player_name_tag = meta_div.find('h1')
            player_name = player_name_tag.get_text(strip=True) if player_name_tag else "Unknown"

            # Step 4: Iterate through the <p> tags to find the citizenship
            citizenships = []
            citizenship_paragraph = None
            
            for p_tag in meta_div.find_all('p'):
                strong_tag = p_tag.find('strong')
                if strong_tag and ('Citizenship' in strong_tag.get_text() or 'National Team' in strong_tag.get_text()):
                    citizenship_paragraph = p_tag
                    break

            # Step 5: Extract the citizenship from <a> tags inside the found paragraph
            if citizenship_paragraph:
                citizenship_links = citizenship_paragraph.find_all('a')
                for link in citizenship_links:
                    citizenships.append(link.get_text(strip=True))

            # Return the player name and citizenships list
            return player_name, citizenships
        
        else:
            return None, []  # No meta div found
    else:
        return None, []  # No info div found


# Main function to scrape the data and write to CSV
async def scrape_player_data(url):
    count = 0
    len_of_links = 1
    for i in range(50):
        if count ==len_of_links:
            await browser.close()
            break
        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(headless=True)  # Set headless=False if you want to see the browser
                page = await browser.new_page()
                page.set_default_timeout(60000)  # 60 seconds
                await stealth_async(page)

                print(url)
                await page.goto(url, timeout=60000)  # Ensure page navigation has 60 seconds timeout
                await page.wait_for_load_state('networkidle', timeout=60000)  # Set load state timeout

                html_content = await page.content()
                soup = BeautifulSoup(html_content, 'html.parser')
                content = soup.find('div', class_ = 'section_content')
                if content:
                    # Find all <a> tags inside the div with class 'section_content'
                    links = content.find_all('a')
                    len_of_links = len(links)
                    print(f'Number of links: {len_of_links}')

                    # Print each link's href attribute
                    for link in links[count:]:
                        count+=1
                        print(f'Processing link {count} of {len_of_links}')
                        href = link['href']  # Access the href attribute
                        player_url = 'https://fbref.com' + href  # Combine base URL with href
                        print(player_url)
                        # Go to the URL and get the content using Playwright
                        await page.goto(player_url, timeout=60000)  # Set a 60-second timeout for each URL
                        await page.wait_for_load_state('networkidle', timeout=60000)  # Wait for network to be idle with timeout
                        html_content = await page.content()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        player_name, citizenships = get_player_info(soup)
                        if player_name == None:
                            await browser.close()
                            break
                        print(player_name)
                        print(citizenships)
                        national_team = ''
                        if citizenships:
                            national_team = citizenships[0]
                            
                        print(national_team)
                        clubs = get_clubs(soup)
                        print(clubs)
                        trophies = get_trophies_won(soup)
                        print(trophies)
                        awards = get_personal_awards(soup)
                        print(awards)

                        # Scraping additional links for domestic, international, and national team stats
                        split_link = url.split('/')
                        dm_cups_link = f'https://{split_link[2]}/{split_link[3]}/{split_link[4]}/{split_link[5]}/dom_cup/{split_link[6]}-Domestic-Cup-Stats'
                        intnl_cup_link = f'https://{split_link[2]}/{split_link[3]}/{split_link[4]}/{split_link[5]}/intl_cup/{split_link[6]}-International-Cup-Stats'
                        tm_link = f'https://{split_link[2]}/{split_link[3]}/{split_link[4]}/{split_link[5]}/nat_tm/{split_link[6]}-National-Team-Stats'

                        # Domestic cup trophies
                        try:
                            await page.goto(dm_cups_link, timeout=60000)  # Set timeout for each additional link
                            await page.wait_for_load_state('networkidle', timeout=60000)

                            html_content = await page.content()
                            soup = BeautifulSoup(html_content, 'html.parser')
                            domestic_cup_trophies = get_domestic_cup_trophies(soup)
                        except Exception as e:
                            print(f"Error fetching domestic cup trophies: {e}")
                            domestic_cup_trophies = ""

                        # International cup trophies
                        try:
                            await page.goto(intnl_cup_link, timeout=60000)
                            await page.wait_for_load_state('networkidle', timeout=60000)

                            html_content = await page.content()
                            soup = BeautifulSoup(html_content, 'html.parser')
                            international_cup_trophies = get_international_cup_trophies(soup)
                        except Exception as e:
                            print(f"Error fetching international cup trophies: {e}")
                            international_cup_trophies = ""

                        # National team trophies
                        try:
                            await page.goto(tm_link, timeout=60000)
                            await page.wait_for_load_state('networkidle', timeout=60000)

                            html_content = await page.content()
                            soup = BeautifulSoup(html_content, 'html.parser')
                            national_team_trophies = get_national_team_trophies(soup)
                        except Exception as e:
                            print(f"Error fetching national team trophies: {e}")
                            national_team_trophies = ""

                        trophies_combined = f"{trophies} ~ {domestic_cup_trophies} ~ {international_cup_trophies} ~ {national_team_trophies}"

                        try:
                            file_exists = os.path.isfile('player_data_bj.csv')

                            with open('player_data_bj.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                                fieldnames = ['player_name', 'nationality', 'national_team', 'teams', 'trophies', 'awards']
                                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                                # Write header only if the file does not exist
                                if not file_exists:
                                    writer.writeheader()

                                writer.writerow({
                                    'player_name': player_name,
                                    'nationality': citizenships,
                                    'national_team': national_team,
                                    'teams': clubs,
                                    'trophies': trophies_combined,
                                    'awards': awards
                                })
                        except Exception as e:
                            print(f"Error writing to CSV: {e}")
        except Exception as e:
            print(f"Error scraping data from URL: {e}")

# Main entry point to use Playwright for all scraping
for p in players:
    url = f"https://fbref.com/en/players/{p}/"
    asyncio.run(scrape_player_data(url))
