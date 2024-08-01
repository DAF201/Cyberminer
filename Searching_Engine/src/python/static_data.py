from json import load

# loads all the indexed urls for searching
indexed_urls = {}
with open(r"./urls.json") as indexing_file:
    indexed_urls = load(indexing_file)

# search results will be injected into this
searching_result_page_html = """
<!DOCTYPE html>
<html lang="en">
<style>
    body {
        font-family:Arial, Helvetica, sans-serif;
        background-color: #f4f4f4;
        color: #333;
        margin: 0;
        padding: 20px;
    }

    h1 {
        text-align: center;
        margin-bottom: 20px;
    }

    #searching_result_urls {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background: #fff;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
    }

    .result-item {
        margin-bottom: 20px;
    }

    .result-item a {
        font-size: 1.2em;
        color: #0066cc;
        text-decoration: none;
    }

    .result-item a:hover {
        text-decoration: underline;
    }

    .result-item p {
        font-size: small;
        color: #666;
    }
</style>

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Result</title>

</head>

<body>
    <h1>Searching Results%s</h1>
    <div id="searching_result_urls">
        %s
    </div>
</body>

</html>
"""
