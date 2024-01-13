import requests
from bs4 import BeautifulSoup
import csv
import re


# # Send a GET request to the website
def get_movie_link_response(movie_link):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    response = requests.get(movie_link, headers=headers)
    return response


def get_movie_details(response):
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # scrapping movie score and number of voters
    rating = soup.find("div", class_="sc-7ab21ed2-0 kkdwNM")
    score = rating.find("span", class_="sc-7ab21ed2-1 eUYAaq").text
    voters = rating.find("div", class_="sc-7ab21ed2-3 iDwwZL").text

    # getting the object that contains details about movie genres, director, stars and writers
    details = soup.find("div", class_="sc-849ec3ff-4 ceCuFh")

    # scrapping movie genres
    try:
        summary_box = details.find("div", class_="sc-16ede01-8 iQfvoj sc-849ec3ff-11 dhFeDs")
        genres_box = summary_box.find("div", {"data-testid": "genres"})
        genres_list = genres_box.find("div", class_="ipc-chip-list__scroller")
        genres_links = genres_list.findAll("span", class_="ipc-chip__text")
        genres = []
        for genre in genres_links:
            genres.append(genre.text)
    except:
        genres = ["Action"]

    # scrapping movie director and stars
    try:
        staff_details = details.find("div", class_="sc-fa02f843-0 iDXoEx")
        staff_ul = staff_details.find("ul",
                                      class_="ipc-metadata-list ipc-metadata-list--dividers-all title-pc-list ipc-metadata-list--baseAlt")
        div_list = staff_ul.findAll("div", class_="ipc-metadata-list-item__content-container")
        # print(div_list[0])
        director = div_list[0].find("a",
                                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link").text
        stars_links = div_list[2].findAll("a",
                                          class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")
        stars = []
        for star in stars_links:
            stars.append(star.text)
    except:
        director = "majid"
        stars = ["majid"]

    # getting the object that contains details about country of origin and language
    # movie_details = soup.find("section", {"data-testid": "Details"})
    movie_details = soup.find("div", {"data-testid": "title-details-section"})
    # scrapping language and country
    try:
        movie_Detail_ul = movie_details.find("ul",
                                             class_="ipc-metadata-list ipc-metadata-list--dividers-all ipc-metadata-list--base")
        movie_Detail_li = movie_Detail_ul.findAll("li", class_="ipc-metadata-list__item")
        # scrapping counties
        country_links = movie_Detail_li[1].findAll("a",
                                                   class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")
        countries = []
        for country in country_links:
            countries.append(country.text)
    except:
        countries = ["United states"]

    # scrapping language
    try:
        language_links = movie_Detail_li[3].findAll("a",
                                                    class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")
        languages = []
        for language in language_links:
            languages.append(language.text)
    except:
        languages = ["N/A"]

    # scrapping budget
    try:
        box_office = soup.find("section", {"data-testid": "BoxOffice"})
        box_office_details = box_office.find("ul",
                                             class_="ipc-metadata-list ipc-metadata-list--dividers-none ipc-metadata-list--compact sc-6d4f3f8c-0 VdkJY ipc-metadata-list--base")
        box_office_li = box_office_details.findAll("li", class_="ipc-metadata-list__item sc-6d4f3f8c-2 byhjlB")
        budget_div = box_office_li[0].find("div", class_="ipc-metadata-list-item__content-container")
        budget = budget_div.find("label", class_="ipc-metadata-list-item__list-content-item").text
        budget = budget.split()[0]
    except:
        budget = "N/A"

    return score, voters, genres, director, stars, countries, languages, budget


def concatenate_strings(string_list, linker):
    # Use the join() method to concatenate all strings in the list
    return linker.join(string_list)


def extract_numeric(string):
    try:
        return int(re.sub(r'[^\d]', '', string))
    except:
        return 403


def numerate_number_of_voters(string):
    try:
        if 'M' in string:
            return int(float(string.replace('M', '')) * 1000000)
        elif 'K' in string:
            return int(float(string.replace('K', '')) * 1000)
        else:
            return int(string)
    except:
        return 403


def main():
    url = "https://www.imdb.com/chart/top"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")


    # Find all the movies on the page
    movies = soup.find_all("td", class_="titleColumn")

    # Create a new csv file and write the headers
    with open("imdb.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Rank", "Title", "Year", "rating", "number_of_votes", "genres",
                                                     "director", "stars", "countries", "languages", "budget"])
        writer.writeheader()
        for i, movie in enumerate(movies):
            title = movie.a.text
            title = title.replace(",", '')
            if title.isnumeric():
                title = str(title) + 'm'

            year = movie.span.text[1:5]
            link = "https://www.imdb.com" + movie.a["href"]
            response = get_movie_link_response(link)
            score, voters, genres, director, stars, countries, languages, budget = get_movie_details(response)

            genres = concatenate_strings(genres, ' ')

            for j in range(len(stars)):
                stars[j] = concatenate_strings(stars[j].split(), "_")
            stars = concatenate_strings(stars, ' ')

            for j in range(len(countries)):
                countries[j] = concatenate_strings(countries[j].split(), "_")
            countries = concatenate_strings(countries, ' ')

            languages = concatenate_strings(languages, ' ')
            if not languages.strip():
                languages = "English"

            budget = extract_numeric(budget)
            year = int(year)
            score = float(score)
            voters = numerate_number_of_voters(voters)

            writer.writerow({"Rank":i+1, "Title":title, "Year":year, "rating":score, "number_of_votes": voters,
                             "genres":genres, "director":director, "stars":stars, "countries":countries,
                             "languages":languages, "budget":budget})


main()

