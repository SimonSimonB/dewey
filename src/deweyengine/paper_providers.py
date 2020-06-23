import re
import pathlib
import pdfminer.high_level
import requests
import urllib
import selenium.webdriver
import pathlib

CACHED_PAPERS_PATH = pathlib.Path('./dewey/cached_papers/')

def _get_html(url):
    #page = requests.get(url)
    #return str(page.text)

    options = selenium.webdriver.chrome.options.Options()
    options.headless = True
    driver = selenium.webdriver.Chrome(chrome_options=options)

    driver.get(url)
    page_source = driver.page_source
    return page_source

def _get_html_and_visible_text(url, css_selector):
    """
    Returns HTML at the given URL as well as visible text in the specified element, or '' if no such element exists.
    """
    options = selenium.webdriver.chrome.options.Options()
    options.headless = True
    driver = selenium.webdriver.Chrome(chrome_options=options)
    driver.get(url)

    try: 
        element = driver.find_element_by_css_selector(css_selector)
        element = element.text
    except selenium.common.exceptions.NoSuchElementException:
        element = ''

    return driver.page_source, element

def _cache_paper_body(doi, body):
    # Cache the body in a txt file
    txt_path = CACHED_PAPERS_PATH / (doi.replace('/', '-slash-') + '.txt')
    if not txt_path.exists():
        with open(str(txt_path), 'w+', encoding='utf-8') as f:
            f.write(body)

def _download_and_cache_pdf(doi, pdf_url):
    pdf_path = CACHED_PAPERS_PATH / (doi.replace('/', '-slash-') + '.pdf')

    # Download PDF to file if it is not cached.
    if not pdf_path.exists():
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        pdf_req_response = requests.get(pdf_url, headers=headers)

        CACHED_PAPERS_PATH.mkdir(exist_ok='True')
        with open(str(pdf_path), 'wb') as f:
            f.write(pdf_req_response.content)

    # Extract text from PDF
    pdf_text = pdfminer.high_level.extract_text(str(pdf_path))

    # pdfminer will extract \ngovernment if government starts at a newline. Remove the '\n' everywhere.
    pdf_text = pdf_text.replace('\n', ' ')

    # pdfminer will extract con- tractualism if the word is split up across two lines.
    pdf_text = pdf_text.replace('-  ', '')

    return pdf_text

def ethics_papers(exclude_dois=None, most_recent_year=None):
    # Get URLs of all the different issues (starting from XXXX, because there are no abstracts before then).
    all_issues_source = _get_html('https://www.journals.uchicago.edu/loi/et')
    issue_urls = re.findall(r'.*(https://www.journals.uchicago.edu/toc/et/[^\"]+).*', all_issues_source)

    if most_recent_year:
        issue_urls = [issue_url for issue_url in issue_urls if int(issue_url.split('https://www.journals.uchicago.edu/toc/et/')[1][:4]) <= most_recent_year]

    for issue_url in issue_urls:
        issue_source = _get_html(issue_url)

        # Extract subsection which lists articles (rather than book reviews, etc.)
        # but if there are none (e.g. because the whole issue is a book symposium), skip
        if r'"subject heading-1">Article' not in issue_source:
            continue

        issue_source = issue_source.split(r'"subject heading-1">Article')[1]
        issue_source = issue_source.split(r'"subject heading-1"')[0]

        # Extract DOIs of articles
        dois = [m.start() for m in re.finditer('/doi/abs', issue_source)]
        dois = [issue_source[start+9:start+30].split(r'"')[0] for start in dois]

        if exclude_dois is not None:
            dois = [doi for doi in dois if not doi in exclude_dois]

        # Retrieve data about each paper
        for doi in dois:
            source, body = _get_html_and_visible_text('https://www.journals.uchicago.edu/doi/full/' + doi, 'article.article')
            body = body.replace('\n', ' ')

            title = re.search(r'meta name=\"dc.Title\" content=\"([^\"]+)', source).groups()[0]

            author = ''
            if r'meta name="dc.Creator" content=' in source:
                for contributor in re.findall(r'meta name=\"dc.Creator\" content=\"([^\"]+)', source):
                    author += contributor.strip() + ', '
            else:
                for contributor in re.findall(r'meta name=\"dc.Contributor\" content=\"([^\"]+)', source):
                    author += contributor.strip() + ', '
            author = author[:-2]

            abstract = re.search(r'meta name=\"dc.Description\" content=\"([^\"]+)', source).groups()[0]
            year = int(re.search(r'meta name=\"dc.Date\" scheme=\"WTN8601\" content=\"([^-]+)', source).groups()[0])

            # Extract the body of the paper
            if len(body) < 1000:
                pdf_url = 'https://www.journals.uchicago.edu/doi/pdfplus/' + doi
                body = _download_and_cache_pdf(doi, pdf_url)

            #if r'class="fulltext"' in source:
                # Extract body from HTML
            #    body = source[source.find(r'class="fulltext"'):source.find('article>')]
            #else:
            #    pdf_url = 'https://www.journals.uchicago.edu/doi/pdfplus/' + doi
            #    body = _download_and_cache_pdf(doi, pdf_url)

            _cache_paper_body(doi, body)

            if len(body) < 1000:
                raise RuntimeError(f'The paper body is less than 1000 characters long, so I guess that I failed to extract the full paper body. That is the body I extracted: \n {body}')

            yield {'title': title, 'author': author, 'abstract': abstract, 'year': year, 'doi': doi, 'journal': 'Ethics', 'body': body}
    
def ppa_papers(exclude_dois=None, most_recent_year=2020):
    for year in range(most_recent_year, 1994-1, -1):
        year_html = _get_html('https://onlinelibrary.wiley.com/loi/10884963/year/' + str(year))

        issue_urls = re.findall(r'a href=\"(/toc/10884963/' + str(year) + '[^\"]+)', year_html)
        issue_urls = {'https://onlinelibrary.wiley.com' + issue_url for issue_url in issue_urls}

        for issue_url in issue_urls:
            issue_html = _get_html(issue_url)

            # If the page contains a subheading "Original articles", extract that part of the HTML.
            # (If the page does not contain a subheading "Original articles", then all links on the page with the name "Full text" will point to papers.)
            if 'Original Article' in issue_html:
                issue_html = issue_html[issue_html.find(r'title="Original Article'):]
                # If there is another section, after the original articles, remove that.
                if 'heading-level-1-' in issue_html:
                    issue_html = issue_html[:issue_html.find('heading-level-1-')]
                
            dois = re.findall(r'Full text[^\"]+\" href=\"/doi/full/([^\"]+)', issue_html)

            if exclude_dois is not None:
                dois = [doi for doi in dois if not doi in exclude_dois]
            
            for doi in dois:
                #full_paper_html = _get_html('https://onlinelibrary.wiley.com/doi/full/' + doi)
                full_paper_html, body = _get_html_and_visible_text('https://onlinelibrary.wiley.com/doi/full/' + doi, 'section.article-section__full')

                if 'Get access to the full version' in full_paper_html:
                    raise Exception(f'Paper {doi} is behind a paywall. Are you connected via institutional VPN?')
                
                author = ''
                for paper_author in re.findall(r'meta name=\"citation_author\" content=\"([^\"]+)', full_paper_html):
                    author += paper_author.strip() + ', '
                author = author[:-2]

                title = re.search(r'meta name=\"citation_title\" content=\"([^\"]+)', full_paper_html).groups()[0]
                year = int(re.search(r'meta name=\"citation_publication_date\" content=\"(....)([^\"]+)', full_paper_html).groups()[0])
                #body = full_paper_html[full_paper_html.find('article-section article-section__full'):full_paper_html.find('custom-style-list noteList')]

                # If the extracted body is empty or very short, then it is not displayed in the HTML. Then, download PDF.
                if len(body) < 1000:
                    pdf_url = 'https://onlinelibrary.wiley.com/doi/pdfdirect/' + doi
                    body = _download_and_cache_pdf(doi, pdf_url)
                
                # Remove newlines
                body = body.replace('\n', ' ')

                _cache_paper_body(doi, body)

                yield {'title': title, 'author': author, 'abstract': '', 'year': year, 'doi': doi, 'journal': 'Philosophy & Public Affairs', 'body': body}



#if __name__ == '__main__':
    #next(ppa_papers())
    # with open('ethics_fullpage_contributors.html', 'r', encoding='utf-8') as f:
    #     source = f.read()
    #     title = re.search(r'meta name=\"dc.Title\" content=\"([^\"]+)', source).groups()[0]

    #     author = ''
    #     if r'meta name="dc.Creator" content=' in source:
    #         for contributor in re.findall(r'meta name=\"dc.Creator\" content=\"([^\"]+)', source):
    #             author += contributor.strip() + ', '
    #     else:
    #         for contributor in re.findall(r'meta name=\"dc.Contributor\" content=\"([^\"]+)', source):
    #             author += contributor.strip() + ', '
    #     author = author[:-2]

    #     abstract = re.search(r'meta name=\"dc.Description\" content=\"([^\"]+)', source).groups()[0]
    #     year = re.search(r'meta name=\"dc.Date\" scheme=\"WTN8601\" content=\"([^-]+)', source).groups()[0]

    #     # Extract the body of the paper, either from the HTML or, if only a PDF is available, from the PDF.
    #     if r'class="fulltext"' in source:
    #         # Extract body from HTML
    #         body = source[source.find(r'class="fulltext"'):source.find('article>')]

    #         # Cache the body in a txt file
    #         txt_path = CACHED_PAPERS_PATH / (doi.replace('/', '-slash-') + '.txt')
    #         if not txt_path.exists():
    #             with open(str(txt_path), 'w+', encoding='utf-8') as f:
    #                 f.write(body)
    #     else:
    #         pdf_path = CACHED_PAPERS_PATH / (doi.replace('/', '-slash-') + '.pdf')

    #         # Download PDF to file if it is not cached.
    #         if not pdf_path.exists():
    #             pdf_link = 'https://www.journals.uchicago.edu/doi/pdfplus/' + doi
    #             pdf_req_response = requests.get(pdf_link)

    #             CACHED_PAPERS_PATH.mkdir(exist_ok='True')
    #             with open(str(pdf_path), 'wb') as f:
    #                 f.write(pdf_req_response.content)

    #         # Extract text from PDF
    #         body = pdfminer.high_level.extract_text(str(pdf_path))

    #     paper = {'title': title, 'author': author, 'abstract': abstract, 'year': year, 'doi': doi, 'journal': 'Ethics', 'body': body}


    # doi = '10.1086/233370'
    # pdf_path = CACHED_PAPERS_PATH / (doi.replace('/', '-slash-') + '.pdf')

    # # Download PDF to file if it is not cached.
    # if not pdf_path.exists():
    #     pdf_link = 'https://www.journals.uchicago.edu/doi/pdfplus/' + doi
    #     response = requests.get(pdf_link)

    #     CACHED_PAPERS_PATH.mkdir(exist_ok='True')
    #     with open(str(pdf_path), 'wb') as f:
    #         f.write(response.content)

    # # Extract text from PDF
    # body = pdfminer.high_level.extract_text(str(pdf_path))

    # with open(r'C:\Users\simon\Coding\ML\FindSimilarPapers\ethics_fullpage_example.html', 'r', encoding='utf8') as f:
    #     source = f.read()
    #     print(len(source))
    #     title = re.search(r'meta name=\"dc.Title\" content=\"([^\"]+)', source).groups()[0]
    #     author = re.search(r'meta name=\"dc.Creator\" content=\"([^\"]+)', source).groups()[0]
    #     abstract = re.search(r'meta name=\"dc.Description\" content=\"([^\"]+)', source).groups()[0]
    #     year = re.search(r'meta name=\"dc.Date\" scheme=\"WTN8601\" content=\"([^-]+)', source).groups()[0]
    #     body = source[source.find(r'class="fulltext"'):source.find('article>')]

    # next(ethics_papers())