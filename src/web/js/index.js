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
        let resultCards = [];

        for (const paper of this.props.papers || []) {
            resultCards.push(
                ResultCard(paper)
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

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            papers: null,
        }
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
                    appElement.setState({ papers: response });
                }
            };
        }
    }

    render() {
        return (
            <div id='wrapper'>
                <InputBox onKeyDown={(e) => this.query(e)} />
                <Results papers={this.state.papers} />
            </div>
        );
    }
}

ReactDOM.render(
    <App />,
    document.getElementById('root')
);