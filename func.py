import datetime
import pytz
import urllib.request
from bs4 import BeautifulSoup
from tika import parser


# some useful functions for parsing
# timestamp for parsing date
def create_timestamp():
    # This timestamp is in UTC
    my_ct = datetime.datetime.now(tz=pytz.UTC)
    tz = pytz.timezone('Europe/Kiev')
    # Now convert it to another timezone
    new_ct = my_ct.astimezone(tz)
    timestamp = new_ct.strftime("%d-%m-%Y_%H-%I")
    return timestamp

# create results in a csv file
def create_csv(df, filename):
    file_timestamp = create_timestamp()
    csv_file = df.to_csv(f'result_csv/{filename}_{file_timestamp}.csv', index=False, encoding='utf-8')
    return csv_file


# URL request function
def url_request(url):
    # http://www.networkinghowtos.com/howto/common-user-agent-list/
    HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Accept-Language': 'uk-UA, ukr;q=0.5'})
    request = urllib.request.Request(url, headers=HEADERS)
    response = urllib.request.urlopen(request, timeout=5)
    status_code = response.status
    print(f'Status code {status_code}')

    # if no error, then read the response contents
    if 200 <= status_code < 300:
    # read the data from the URL
        data_response = response.read().decode("utf8")
    return data_response

# Function for reading pdf files
def read_pdf(filename):
    file = parser.from_file(filename)
    return(file)

# Function for cleaning raw text
def cleaning_raw_text(text_strings):
    safe_text = text_strings.encode('utf-8', errors='ignore')
    safe_text = safe_text.decode('utf-8')
    clean_text = str(safe_text).replace("\nn", "\n")
    clean_text = str(clean_text).replace("\nnn", "\n")
    clean_text = str(clean_text).replace("\n\n\n\n\n", "\n")
    clean_text = str(clean_text).replace("\n\n\n\n", "\n")
    clean_text = str(clean_text).replace("\n\n\n", "\n")
    clean_text = str(clean_text).replace("\n\n", "\n")
    clean_text = str(clean_text).replace("\n\n", "\n")
    clean_text = str(clean_text).replace("-----", "-")
    clean_text = str(clean_text).replace("----", "-")
    clean_text = str(clean_text).replace("---", "-")
    clean_text = ''.join(clean_text.split('\n', 1))
    return clean_text


def htmlToText(html):
    soup = BeautifulSoup(html, 'lxml')
    # removing scripts, styles and other useless tags
    [element.extract() for element in soup(['style', 'script', 'meta', '[document]', 'head', 'title'])]
    # getting text from html
    text = soup.getText()
    return text


def read_html(filename):
    file = parser.from_file(filename)
    return (file)


html_content_list = []

def read_html_files(path=None):
    if path is not None:
        for i, file in enumerate(path):
            # creating an object
            try:
                text = read_html(file)
                t = [[k, v] for k, v in text.items()]
                # print(t)
                text_strings = str(t[1][1])

            except Exception:
                print(f"Something is wrong with reading HTML file #{i}")
                continue
            html_content_list.append(cleaning_raw_text(text_strings))



