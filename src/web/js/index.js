function ResultCard(paper) {
    return (
        <div key={paper.doi}>
            <a href={'https://doi.org/' + paper.doi} className='card'>
                <card-content-left>
                    <h1 className='papertitle'>{paper.title}</h1>
                    <span className='paperauthor'>{paper.author}</span>
                    <span className='paperjournalyear'><i>{paper.journal}</i>, {paper.year}</span>
                </card-content-left>
                <card-content-right>
                    {paper.abstract}
                </card-content-right>
            </a>
        </div>
    );
}

class Results extends React.Component {
    render() {
        let startIndex = Math.max(0, this.props.currentPage - 1) * this.props.resultsPerPage;
        let endIndex = Math.min(this.props.papers.length - 1, startIndex + this.props.resultsPerPage - 1);
        let resultCards = [];

        for (let i = startIndex; i <= endIndex; i++) {
            resultCards.push(
                ResultCard(this.props.papers[i])
            );
        }

        return (
            <div id='results'>
                {resultCards}
            </div>
        );
    }
}

class InputBox extends React.Component {
    render() {
        return (
            <textarea name='query' id='searchbox'
                placeholder='Type or paste keywords, abstracts, or entire papers.&#10;&#10;Press enter to search.' rows='5'
                form='searchnow'
                onKeyDown={(e) => this.props.onKeyDown(e)}>
            </textarea>
        );
    }
}

class ResultsNavigation extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {

        let navigationButtons = [];

        let i = this.props.minPage;
        for (; i <= this.props.maxPage; i++) {
            navigationButtons.push(
                <button key={i} onClick={this.props.handleClick} className='resultsnavigationbutton'>{i}</button>
            );
        }

        return (
            <div id='buttoncontainer'>
                {navigationButtons}
            </div>
        );
    }
}

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            papers: [],
            resultsPerPage: 10,
            currentPage: null,
            minPage: null,
            maxPage: null,
        };

        this.handlePageNavClick = this.handlePageNavClick.bind(this);
    }

    handlePageNavClick(event) {
        const destinationPage = parseInt(event.target.textContent);
        this.setState({ currentPage: destinationPage });

        // Scroll up when the user navigates to a different page of the results.
        document.body.scrollTop = 0;
        document.documentElement.scrollTop = 0;
    }

    query(event) {
        const SEARCH_URI = 'http://127.0.0.1:8080/similarpapers';

        if (event.key == 'Enter') {
            event.preventDefault();

            let xhr = new XMLHttpRequest();
            xhr.open('POST', SEARCH_URI, true);
            xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
            const query = { 'query': event.target.value }
            xhr.send(JSON.stringify(query));

            // Display the JSON response from the server.
            let appElement = this;
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    appElement.setState({
                        papers: response,
                        currentPage: 1,
                        minPage: 1,
                        maxPage: Math.floor((response.length - 1) / appElement.state.resultsPerPage) + 1
                    });
                }
            };
        }
    }

    render() {
        return (
            <div id='wrapper'>
                <InputBox onKeyDown={(e) => this.query(e)} />
                <Results papers={this.state.papers} resultsPerPage={this.state.resultsPerPage} currentPage={this.state.currentPage} />
                <ResultsNavigation
                    handleClick={this.handlePageNavClick}
                    currentPage={this.state.currentPage}
                    minPage={this.state.minPage}
                    maxPage={this.state.maxPage}
                />
            </div>
        );
    }
}

ReactDOM.render(
    <App />,
    document.getElementById('root')
);