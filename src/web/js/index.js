const SEARCH_URI = "http://127.0.0.1:8080/similarpapers";
const inputElement = document.getElementById("searchbox")

// If the enter key is pressed, then the query is sent off to the search service.
inputElement.addEventListener("keydown", function (event) {
    if (event.key == "Enter") {
        event.preventDefault();

        let xhr = new XMLHttpRequest();
        xhr.open("POST", SEARCH_URI, true);
        xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
        const query = { "query": inputElement.value }
        xhr.send(JSON.stringify(query));

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                let resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = '';
                for (const paper of response) {
                    // Create an HTML element that shows information about this paper.
                    let paperDiv = document.createElement('div');
                    let paperCard = document.createElement('a');

                    let cardContentLeft = document.createElement('card-content-left');
                    let paperTitle = document.createElement('h1');
                    paperTitle.classList.add('papertitle');
                    paperTitle.innerText = paper['title'];
                    let paperAuthor = document.createElement('span')
                    paperAuthor.classList.add('paperauthor')
                    paperAuthor.innerText = paper['author']
                    let paperJournalYear = document.createElement('span')
                    paperJournalYear.classList.add('paperjournalyear')
                    paperJournalYear.innerHTML = '<i>' + paper['journal'] + '</i>, ' + paper['year'];

                    cardContentLeft.appendChild(paperTitle);
                    cardContentLeft.appendChild(paperAuthor);
                    cardContentLeft.appendChild(paperJournalYear);

                    paperCard.setAttribute('href', 'https://doi.org/' + paper['doi']);
                    paperCard.classList.add('card');
                    paperCard.appendChild(cardContentLeft);

                    let cardContentRight = document.createElement('card-content-right');
                    if (paper['abstract'] != '') {
                        cardContentRight.innerHTML = 'Abstract:<br>' + paper['abstract'];
                    } else if (paper['auto_summary'] != '') {
                        cardContentRight.innerHTML = 'Quotes from the paper:<br>' + paper['auto_summary'];
                    }
                    paperCard.appendChild(cardContentRight);

                    paperDiv.appendChild(paperCard);
                    resultsDiv.appendChild(paperDiv);
                }
            }
        };
    };
});